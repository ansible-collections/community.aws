try:
    import boto3
    from botocore.client import Config
except ImportError:
    pass
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple


class S3ClientManager:
    def __init__(self, connection) -> None:
        self.connection = connection
        self._s3_client = None

    def initialize_s3_client(self, region_name: str, endpoint_url: str, profile_name: str) -> None:
        """
        Create the S3 client inside the manager.
        """
        self._s3_client = self.get_boto_client(
            "s3",
            region_name=region_name,
            endpoint_url=endpoint_url,
            profile_name=profile_name,
        )

    def get_bucket_endpoint(self) -> Tuple[str, str]:
        """
        Fetches the correct S3 endpoint and region for use with our bucket.
        If we don't explicitly set the endpoint then some commands will use the global
        endpoint and fail.
        """
        region_name = self.connection.get_option("region") or "us-east-1"
        profile_name = self.connection.get_option("profile") or ""
        self.connection._vvvv("_get_bucket_endpoint: S3 (global)")
        tmp_s3_client = self.get_boto_client(
            "s3",
            region_name=region_name,
            profile_name=profile_name,
        )
        head_bucket = tmp_s3_client.head_bucket(
            Bucket=(self.connection.get_option("bucket_name")),
        )
        bucket_region = head_bucket.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("x-amz-bucket-region", None)
        if bucket_region is None:
            bucket_region = "us-east-1"

        if self.connection.get_option("bucket_endpoint_url"):
            return self.connection.get_option("bucket_endpoint_url"), bucket_region

        self.connection._vvvv(f"_get_bucket_endpoint: S3 (bucket region) - {bucket_region}")
        s3_bucket_client = self.get_boto_client(
            "s3",
            region_name=bucket_region,
            profile_name=profile_name,
        )

        return s3_bucket_client.meta.endpoint_url, s3_bucket_client.meta.region_name

    def get_boto_client(
        self,
        service: str,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ) -> Any:
        """Gets a boto3 client based on the STS token"""

        aws_access_key_id = self.connection.get_option("access_key_id")
        aws_secret_access_key = self.connection.get_option("secret_access_key")
        aws_session_token = self.connection.get_option("session_token")

        session_args = dict(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
        )
        if profile_name:
            session_args["profile_name"] = profile_name
        session = boto3.session.Session(**session_args)

        client = session.client(
            service,
            endpoint_url=endpoint_url,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": self.connection.get_option("s3_addressing_style")},
            ),
        )
        return client

    def get_url(
        self,
        client_method: str,
        bucket_name: str,
        out_path: str,
        http_method: str,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate URL for get_object / put_object"""

        client = self._s3_client
        params = {"Bucket": bucket_name, "Key": out_path}
        if extra_args is not None:
            params.update(extra_args)
        return client.generate_presigned_url(client_method, Params=params, ExpiresIn=3600, HttpMethod=http_method)

    def generate_encryption_settings(self) -> Tuple[Dict, Dict]:
        """Generate Encryption Settings"""
        put_args = {}
        put_headers = {}
        if not self.connection.get_option("bucket_sse_mode"):
            return put_args, put_headers

        put_args["ServerSideEncryption"] = self.connection.get_option("bucket_sse_mode")
        put_headers["x-amz-server-side-encryption"] = self.connection.get_option("bucket_sse_mode")
        if self.connection.get_option("bucket_sse_mode") == "aws:kms" and self.connection.get_option(
            "bucket_sse_kms_key_id"
        ):
            put_args["SSEKMSKeyId"] = self.connection.get_option("bucket_sse_kms_key_id")
            put_headers["x-amz-server-side-encryption-aws-kms-key-id"] = self.connection.get_option(
                "bucket_sse_kms_key_id"
            )
        return put_args, put_headers
