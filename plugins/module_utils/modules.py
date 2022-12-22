# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.common import set_collection_info


COMMUNITY_AWS_COLLECTION_NAME = "community.aws"
COMMUNITY_AWS_COLLECTION_VERSION = "6.0.0-dev0"


class AnsibleCommunityAWSModule(AnsibleAWSModule):

    def __init__(self, **kwargs):

        super(AnsibleCommunityAWSModule, self).__init__(**kwargs)
        set_collection_info(
            collection_name=COMMUNITY_AWS_COLLECTION_NAME,
            collection_version=COMMUNITY_AWS_COLLECTION_VERSION,
        )
