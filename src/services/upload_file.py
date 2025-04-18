import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service class for handling file uploads to Cloudinary.

    Attributes:
        cloud_name (str): The Cloudinary cloud name.
        api_key (str): The Cloudinary API key.
        api_secret (str): The Cloudinary API secret.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the UploadFileService with Cloudinary credentials and configure the client.

        Args:
            cloud_name (str): Cloudinary cloud name.
            api_key (str): Cloudinary API key.
            api_secret (str): Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        # Configure Cloudinary with provided credentials
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload a file to Cloudinary and generate a URL for the uploaded image.

        Args:
            file: The file object to upload (should have a .file attribute).
            username (str): The username used to structure the public ID.

        Returns:
            str: The URL of the uploaded and transformed image.
        """
        public_id = f"RestApp/{username}"
        # Upload the file to Cloudinary with the specified public ID and overwrite enabled
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        # Build a URL for the uploaded image with resizing and cropping applied
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
