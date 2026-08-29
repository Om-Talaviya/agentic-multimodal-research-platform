"""Image parser using ModelGateway and VisionProvider."""

import base64
from typing import BinaryIO, List, Optional, Union
from uuid import uuid4
from ai.gateway.model_gateway import ModelGateway
from ai.providers.base import VisionProvider
from ai.providers.router import ModelRouter
from ai.schemas import VisionRequest
from ingestion.parsers.base import DocumentParser, ImageRef, ParsedDocument
from shared.logging import get_logger
from shared.types import DocumentFormat

logger = get_logger(__name__)


class ImageParser(DocumentParser):
    """Parse images using vision models via ModelGateway or ModelRouter."""

    @property
    def supported_formats(self) -> List[DocumentFormat]:
        return [DocumentFormat.IMAGE]

    def __init__(self, vision_source: Optional[Union[ModelGateway, ModelRouter, VisionProvider]] = None) -> None:
        self.vision_source = vision_source

    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        image_data = file.read()
        mime_type = self._get_mime_type(filename)
        b64_image = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_image}"

        prompt = (
            "Describe this image in detail. Extract any visible text (OCR), tables, charts, "
            "diagrams, or structured information with high accuracy."
        )

        content = ""
        model_name = "vision_model"

        if self.vision_source is not None:
            vision_req = VisionRequest(
                images=[data_url],
                prompt=prompt,
            )

            try:
                if isinstance(self.vision_source, ModelGateway):
                    vision_resp = await self.vision_source.analyze_vision(vision_req)
                    content = vision_resp.content
                    model_name = vision_resp.model
                elif isinstance(self.vision_source, ModelRouter):
                    provider = self.vision_source.select_vision()
                    vision_resp = await provider.analyze(vision_req)
                    content = vision_resp.content
                    model_name = vision_resp.model
                elif isinstance(self.vision_source, VisionProvider):
                    vision_resp = await self.vision_source.analyze(vision_req)
                    content = vision_resp.content
                    model_name = vision_resp.model
            except Exception as e:
                logger.warning("Vision model analysis failed during image parsing", filename=filename, error=str(e))
                content = f"[Image: {filename}] (Vision extraction failed: {str(e)})"
        else:
            content = f"[Image: {filename}] (No vision provider configured)"

        image_ref = ImageRef(
            id=str(uuid4()),
            data=image_data,
            mime_type=mime_type,
            caption=filename,
            metadata={"size_bytes": len(image_data), "model": model_name},
        )

        return ParsedDocument(
            content=content,
            metadata={
                "format": "image",
                "filename": filename,
                "mime_type": mime_type,
                "model": model_name,
            },
            images=[image_ref],
        )

    def _get_mime_type(self, filename: str) -> str:
        ext = filename.lower().split(".")[-1]
        mime_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "gif": "image/gif",
            "bmp": "image/bmp",
        }
        return mime_map.get(ext, "image/png")
