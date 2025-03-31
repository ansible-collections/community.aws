# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from io import StringIO
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest

from ansible.errors import AnsibleError
from ansible.playbook.play_context import PlayContext
from ansible.plugins.loader import connection_loader

from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3

from ansible_collections.community.aws.plugins.connection.aws_ssm import Connection
from ansible_collections.community.aws.plugins.plugin_utils.s3clientmanager import S3ClientManager
from ansible_collections.community.aws.plugins.plugin_utils.s3clientmanager import generate_encryption_settings

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip("test_data_pipeline.py requires the python modules 'boto3' and 'botocore'")


class TestConnectionBaseClass:
    @patch(
        "ansible_collections.community.aws.plugins.plugin_utils.s3clientmanager.S3ClientManager.get_bucket_endpoint",
        return_value=("fake-s3-endpoint", "fake-region"),
    )
    def test_init_clients(self, mock_get_bucket_endpoint):
        pc = PlayContext()
        new_stdin = StringIO()
        conn = connection_loader.get("community.aws.aws_ssm", pc, new_stdin)

        boto_clients = {"ssm": MagicMock(), "s3": MagicMock()}

        def mock_get_boto_client(service, *args, **kwargs):
            return boto_clients.get(service)

        conn._get_boto_client = MagicMock(side_effect=mock_get_boto_client)

        options = {
            "s3_addressing_style": MagicMock(),
            "bucket_endpoint_url": MagicMock(),
            "bucket_name": MagicMock(),
            "access_key_id": MagicMock(),
            "secret_access_key": MagicMock(),
            "session_token": MagicMock(),
            "region": MagicMock(),
            "profile": MagicMock(),
        }

        def mock_get_option(name):
            return options.get(name)

        conn.get_option = MagicMock(side_effect=mock_get_option)
        s3_endpoint_url, s3_region_name = MagicMock(), MagicMock()
        mock_get_bucket_endpoint.return_value = (s3_endpoint_url, s3_region_name)

        conn._init_clients()

        # Validate results
        mock_get_bucket_endpoint.assert_called_once_with(
            bucket_name=options.get("bucket_name"),
            bucket_endpoint_url=options.get("bucket_endpoint_url"),
            access_key_id=options.get("access_key_id"),
            secret_key_id=options.get("secret_access_key"),
            session_token=options.get("session_token"),
            region_name=options.get("region"),
            profile_name=options.get("profile"),
        )

        config = {"signature_version": "s3v4", "s3": {"addressing_style": options.get("s3_addressing_style")}}
        conn._get_boto_client.assert_has_calls(
            [
                call("s3", endpoint_url=s3_endpoint_url, region_name=s3_region_name, config=config),
                call("ssm", region_name=options.get("region"), config=config),
            ]
        )
        assert conn.s3_manager.client == boto_clients["s3"]
        assert conn._client == boto_clients["ssm"]

    # XXX This isn't doing anything
    # def test_plugins_connection_aws_ssm_get_url(self):
    #     pc = PlayContext()
    #     new_stdin = StringIO()
    #     connection_loader.get('community.aws.aws_ssm', pc, new_stdin)
    #     boto3 = MagicMock()
    #     boto3.client('s3').return_value = MagicMock()
    #     boto3.generate_presigned_url.return_value = MagicMock()
    #     return (boto3.generate_presigned_url.return_value)

    @patch("os.path.exists")
    def test_plugins_connection_aws_ssm_put_file(self, mock_ospe):
        pc = PlayContext()
        new_stdin = StringIO()
        conn = connection_loader.get("community.aws.aws_ssm", pc, new_stdin)
        conn._connect = MagicMock()
        conn._file_transport_command = MagicMock()
        conn._file_transport_command.return_value = (0, "stdout", "stderr")
        conn.put_file("/in/file", "/out/file")

    def test_plugins_connection_aws_ssm_fetch_file(self):
        pc = PlayContext()
        new_stdin = StringIO()
        conn = connection_loader.get("community.aws.aws_ssm", pc, new_stdin)
        conn._connect = MagicMock()
        conn._file_transport_command = MagicMock()
        conn._file_transport_command.return_value = (0, "stdout", "stderr")
        conn.fetch_file("/in/file", "/out/file")

    @patch("subprocess.check_output")
    @patch("boto3.client")
    def test_plugins_connection_file_transport_command(self, boto_client, s_check_output):
        pc = PlayContext()
        new_stdin = StringIO()
        conn = connection_loader.get("community.aws.aws_ssm", pc, new_stdin)
        conn.get_option = MagicMock()
        conn.get_option.side_effect = ["1", "2", "3", "4", "5"]
        conn._get_url = MagicMock()
        conn._get_url.side_effect = ["url1", "url2"]
        boto3 = MagicMock()
        boto3.client("s3").return_value = MagicMock()
        conn.get_option.return_value = 1
        get_command = MagicMock()
        put_command = MagicMock()
        conn.exec_command = MagicMock()
        conn.exec_command.return_value = (put_command, None, False)
        conn.download_fileobj = MagicMock()
        conn.exec_command(put_command, in_data=None, sudoable=False)
        conn.exec_command(get_command, in_data=None, sudoable=False)

    @patch("subprocess.check_output")
    def test_plugins_connection_aws_ssm_close(self, s_check_output):
        pc = PlayContext()
        new_stdin = StringIO()
        conn = connection_loader.get("community.aws.aws_ssm", pc, new_stdin)
        conn.instance_id = "i-12345"
        conn._session_id = True
        conn.get_option = MagicMock()
        conn.get_option.side_effect = ["/abc", "pqr"]
        conn._session = MagicMock()
        conn._session.terminate = MagicMock()
        conn._session.communicate = MagicMock()
        conn._terminate_session = MagicMock()
        conn._terminate_session.return_value = ""
        conn._session_id = MagicMock()
        conn._session_id.return_value = "a"
        conn._client = MagicMock()
        conn.close()

    def test_generate_mark(self):
        """Testing string generation"""
        test_a = Connection.generate_mark()
        test_b = Connection.generate_mark()

        assert test_a != test_b
        assert len(test_a) == Connection.MARK_LENGTH
        assert len(test_b) == Connection.MARK_LENGTH

    @pytest.mark.parametrize(
        "message,level,method",
        [
            ("test message 1", 1, "v"),
            ("test message 2", 2, "vv"),
            ("test message 3", 3, "vvv"),
            ("test message 4", 4, "vvvv"),
        ],
    )
    def test_verbosity_diplay(self, message, level, method):
        """Testing verbosity levels"""
        play_context = MagicMock()
        play_context.shell = "sh"
        conn = Connection(play_context)
        conn.host = "test-host"  # Test with host set

        with patch("ansible_collections.community.aws.plugins.connection.aws_ssm.display") as mock_display:
            conn.verbosity_display(level, message)
            # Verify the correct display method was called with expected args
            mock_method = getattr(mock_display, method)
            mock_method.assert_called_once_with(message, host="test-host")

            # Test without host set
            conn.host = None
            conn.verbosity_display(1, "no host message")
            mock_display.v.assert_called_with("no host message")

            # Test exception is raised when verbosity level is not an accepted value
            with pytest.raises(AnsibleError):
                conn.verbosity_display("invalid value", "test message")

    def test_poll_verbosity(self):
        """Test poll method verbosity display"""
        pc = PlayContext()
        new_stdin = StringIO()
        conn = connection_loader.get("community.aws.aws_ssm", pc, new_stdin)

        conn._session = MagicMock()
        conn._session.poll.return_value = None
        conn.get_option = MagicMock(return_value=10)  # ssm_timeout
        conn.poll_stdout = MagicMock()
        conn.instance_id = "i-1234567890"
        conn.host = conn.instance_id

        with patch("time.time", return_value=100), patch.object(conn, "verbosity_display") as mock_display:
            poll_gen = conn.poll("TEST", "test command")
            # Advance generator twice to trigger the verbosity message
            next(poll_gen)
            next(poll_gen)

            # Verify verbosity message contains remaining time
            mock_display.assert_called_with(4, "TEST remaining: 10 second(s)")


class TestS3ClientManager:
    """
    Tests for the S3ClientManager class
    """

    def create_object(self):
        self.client = MagicMock()
        return S3ClientManager(self.client)

    @pytest.mark.parametrize("method", ["get", "put", "fake"])
    @pytest.mark.parametrize("is_windows", [False, True])
    @patch("ansible_collections.community.aws.plugins.plugin_utils.s3clientmanager.generate_encryption_settings")
    def test_generate_host_commands(self, m_generate_encryption_settings, method, is_windows):
        """Testing command generation on both Windows and non-Windows systems"""
        s3_client_manager = self.create_object()

        s3_client_manager.get_url = MagicMock()
        s3_client_manager.get_url.return_value = "https://test-url"
        encryption_headers = {"ServerSideEncryption": "aws:kms"}
        encryption_args = MagicMock()
        m_generate_encryption_settings.return_value = (encryption_args, encryption_headers)

        bucket_sse_mode = MagicMock()
        bucket_sse_kms_key_id = MagicMock()
        s3_path = MagicMock()
        bucket_name = MagicMock()

        test_command_generation, put_args = s3_client_manager.generate_host_commands(
            bucket_name=bucket_name,
            bucket_sse_mode=bucket_sse_mode,
            bucket_sse_kms_key_id=bucket_sse_kms_key_id,
            s3_path=s3_path,
            in_path="test/in/path",
            out_path="test/out/path",
            is_windows=is_windows,
            method=method,
        )

        if method not in ("get", "put"):
            assert put_args is None
            test_command_generation is None
        else:
            assert isinstance(test_command_generation, str)
            print(m_generate_encryption_settings.mock_calls)
            if method == "get":
                m_generate_encryption_settings.assert_called_once_with(bucket_sse_mode, bucket_sse_kms_key_id)
                if is_windows:
                    assert test_command_generation.startswith("Invoke-WebRequest -Method PUT -Headers @")
                    assert test_command_generation.endswith(
                        "-InFile 'test/in/path' -Uri 'https://test-url' -UseBasicParsing"
                    )
                else:
                    assert test_command_generation.startswith("curl --request PUT ")
                    assert test_command_generation.endswith("--upload-file 'test/in/path' 'https://test-url'")
                assert put_args == encryption_args
                s3_client_manager.get_url.assert_called_once_with(
                    "put_object", bucket_name, s3_path, "PUT", extra_args=encryption_args
                )
            elif method == "put":
                m_generate_encryption_settings.assert_not_called()
                if is_windows:
                    assert f"Invoke-WebRequest 'https://test-url' -OutFile 'test/out/path'" == test_command_generation
                else:
                    assert "curl -o 'test/out/path' 'https://test-url';touch 'test/out/path'" == test_command_generation
                assert put_args is None
                s3_client_manager.get_url.assert_called_once_with("get_object", bucket_name, s3_path, "GET")

    @pytest.mark.parametrize("bucket_endpoint_url", [None, "bucket_endurl_test"])
    @pytest.mark.parametrize(
        "region_name,bucket_region",
        [
            (None, "eu-west-2"),
            ("us-east-1", "eu-west-2"),
            ("eu-east-1", "eu-west-2"),
            ("eu-west", "eu-west-2"),
        ],
    )
    @patch("ansible_collections.community.aws.plugins.plugin_utils.s3clientmanager.S3ClientManager._get_s3_client")
    def test_get_bucket_endpoint(self, mock__get_s3_client, bucket_endpoint_url, region_name, bucket_region):
        tmp_s3_1 = MagicMock()
        tmp_s3_2 = MagicMock()

        tmp_s3_1.head_bucket = MagicMock(
            return_value={"ResponseMetadata": {"HTTPHeaders": {"x-amz-bucket-region": bucket_region}}}
        )
        tmp_s3_2.head_bucket = MagicMock()

        mock__get_s3_client.side_effect = [tmp_s3_1, tmp_s3_2]

        bucket_name = MagicMock()
        access_key_id = MagicMock()
        secret_key_id = MagicMock()
        session_token = MagicMock()
        profile_name = MagicMock()

        endpoint_url, region = S3ClientManager.get_bucket_endpoint(
            bucket_name=bucket_name,
            bucket_endpoint_url=bucket_endpoint_url,
            access_key_id=access_key_id,
            secret_key_id=secret_key_id,
            session_token=session_token,
            region_name=region_name,
            profile_name=profile_name,
        )

        tmp_s3_1.head_bucket.assert_called_once_with(Bucket=(bucket_name))
        test_region_name = region_name or "us-east-1"
        test_bucket_region = bucket_region or "us-east-1"
        if bucket_endpoint_url:
            assert bucket_endpoint_url == endpoint_url
            assert test_bucket_region == region
            mock__get_s3_client.assert_called_once_with(
                access_key_id, secret_key_id, session_token, test_region_name, profile_name
            )
        elif test_bucket_region == test_region_name:
            assert endpoint_url == tmp_s3_1.meta.endpoint_url
            assert region == tmp_s3_1.meta.region_name
            mock__get_s3_client.assert_called_once_with(
                access_key_id, secret_key_id, session_token, test_region_name, profile_name
            )
        else:
            assert endpoint_url == tmp_s3_2.meta.endpoint_url
            assert region == tmp_s3_2.meta.region_name
            mock__get_s3_client.assert_has_calls(
                [
                    call(access_key_id, secret_key_id, session_token, test_region_name, profile_name),
                    call(access_key_id, secret_key_id, session_token, test_bucket_region, profile_name),
                ]
            )

    def test_get_url_no_extra_args(self):
        """
        Test get_url() without extra_args
        """
        s3_client_manager = self.create_object()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html
        self.client.generate_presigned_url.return_value = "http://test-url-extra"

        result = s3_client_manager.get_url(
            client_method="put_object",
            bucket_name="test_bucket",
            out_path="test/path",
            http_method="PUT",
        )

        expected_params = {"Bucket": "test_bucket", "Key": "test/path"}

        self.client.generate_presigned_url.assert_called_once_with(
            "put_object", Params=expected_params, ExpiresIn=3600, HttpMethod="PUT"
        )
        assert result == "http://test-url-extra"

    def test_get_url_extra_args(self):
        """
        Test get_url() with extra_args
        """
        s3_client_manager = self.create_object()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html
        self.client.generate_presigned_url.return_value = "http://test-url-extra"
        extra_args = {"ACL": "public-read", "ContentType": "text/plain"}

        result = s3_client_manager.get_url(
            client_method="put_object",
            bucket_name="test_bucket",
            out_path="test/path",
            http_method="PUT",
            extra_args=extra_args,
        )

        expected_params = {"Bucket": "test_bucket", "Key": "test/path"}
        expected_params.update(extra_args)

        self.client.generate_presigned_url.assert_called_once_with(
            "put_object", Params=expected_params, ExpiresIn=3600, HttpMethod="PUT"
        )
        assert result == "http://test-url-extra"


@pytest.mark.parametrize(
    "bucket_sse_mode,bucket_sse_kms_key_id,args,headers",
    [
        (None, "We do not care about this", {}, {}),
        (
            "sse_no_kms",
            "sse_key_id",
            {"ServerSideEncryption": "sse_no_kms"},
            {"x-amz-server-side-encryption": "sse_no_kms"},
        ),
        ("aws:kms", "", {"ServerSideEncryption": "aws:kms"}, {"x-amz-server-side-encryption": "aws:kms"}),
        ("aws:kms", None, {"ServerSideEncryption": "aws:kms"}, {"x-amz-server-side-encryption": "aws:kms"}),
        (
            "aws:kms",
            "test_kms_id",
            {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": "test_kms_id"},
            {"x-amz-server-side-encryption": "aws:kms", "x-amz-server-side-encryption-aws-kms-key-id": "test_kms_id"},
        ),
    ],
)
def test_generate_encryption_settings(bucket_sse_mode, bucket_sse_kms_key_id, args, headers):
    """
    Test generate_encryption_settings()
    """

    r_args, r_headers = generate_encryption_settings(bucket_sse_mode, bucket_sse_kms_key_id)
    assert r_args == args
    assert r_headers == headers
