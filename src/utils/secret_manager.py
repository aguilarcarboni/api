from google.cloud import secretmanager
import json
import time
from laserfocus.utils.exception import handle_exception
from laserfocus.utils.logger import logger

@handle_exception
def get_secret(secret_id):
    try:
        logger.info(f"Fetching secret: {secret_id}")

        # Initialize the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Define your project ID and secret name
        project_id = "laser-focused"
        version_id = "1"

        # Build the secret version path
        secret_path = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Fetch the secret (ADC credentials are used here)
        response = client.access_secret_version(request={"name": secret_path})
        
        try:
            logger.info(f"Attempting UTF-8 decode")
            json_string = response.payload.data.decode("UTF-8")
            secrets = json.loads(json_string)
        except Exception as e:
            logger.warning(f"UTF-8 decode failed, trying ASCII")
            try:
                logger.info(f"Attempting ASCII decode")
                json_string = response.payload.data.decode("ascii")
                secrets = json_string
            except Exception as e:
                logger.error(f"All decoding attempts failed")
                raise Exception(f"Error fetching secret: {e}")

        logger.success(f"Successfully fetched and decoded secret")
        return secrets
        
    except Exception as e:
        logger.error(f"Unexpected error while fetching secret")
        raise