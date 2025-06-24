from uuid import uuid4


async def upload_image_to_storage(image_data: bytes, filename_prefix: str) -> str:
    filename = f"{filename_prefix}_{uuid4()}.png"
    print(f"MOCK storage_services: Uploading image data as {filename}")
    return f"https://s3.example.com/mock_images/{filename}"
