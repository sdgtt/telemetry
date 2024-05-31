import os

from telemetry.dev.core import Core


class VPX(Core):
    """VPX Card telemetry functions."""

    _mongo_database = "devboards"
    _mongo_collection = "vpx_washington"
    _minio_bucket = "devboards"
    _minio_subfolder = "vpx_washington"

    def __init__(self, configfilename=None, configs={}):
        project = "vpx"
        configs["mongo"] = {
            "database": self._mongo_database,
            "collection": self._mongo_collection,
        }
        configs["minio"] = {
            "bucket": self._minio_bucket,
            "subfolder": self._minio_subfolder,
        }
        super().__init__(project, configfilename, configs)

    def _check_mongo_and_minio(self):
        if not hasattr(self, "mongo"):
            raise Exception("MongoDB not configured")
        if not hasattr(self, "minio"):
            raise Exception("Minio not configured")

        # Check if bucket exists
        if not self.minio.bucket_exists(self._minio_bucket):
            # Create the bucket
            print(f"Creating bucket {self._minio_bucket}")
            self.minio.make_bucket(self._minio_bucket)

    def submit_test_data(self, job_id: str, metadata: dict, artifact_files: list):
        """Submit test data to MongoDB and Minio.

        Data organization:
        - MongoDB:
            - Overview: Database/Collection/Document
            - Namings:
                - Jenkins test: devboards/vpx_washington/j<job_id>-<hdl_hash>-<linux_hash>
                - Manual test: devboards/vpx_washington/m<test_start_time>-<hdl_hash>-<linux_hash>
        - Minio:
            - Overview: Bucket/Subfolder/File
            - Namings:
                - Jenkins test: devboards/vpx_washington/j<job_id>-h<hdl_hash>-s<linux_hash>/<artifact_files>
                - Manual test: devboards/vpx_washington/m<test_start_time>-h<hdl_hash>-s<linux_hash>/<artifact_files>

        Args:
            job_id (str): Jenkins job ID. If manual use form "m<test_start_time>".
            metadata (dict): Test metadata.
            artifact_files (list): List of artifact files.
        """
        ## Checks
        # Check if metadata has required fields
        required_fields = ["junit_xml", "hdl_hash", "linux_hash", "test_date"]
        for field in required_fields:
            if field not in metadata:
                raise Exception(f"metadata missing field {field}")

        # Check if files exist
        for file in artifact_files:
            if not os.path.isfile(file):
                raise Exception(f"File {file} does not exist")

        # Check job ID format
        if not job_id.startswith("j") and not job_id.startswith("m"):
            raise Exception(
                "Job ID must start with 'j' for Jenkins job or 'm' for manual test"
            )
        if job_id.startswith("j") and not job_id[1:].isdigit():
            raise Exception("Job ID must have a numerical value after the 'j'")
        if job_id.startswith("m"):
            date_str = job_id[1:]
            # Must be a valid date of form YYYYMMDD_HHMMSS
            if len(date_str) != 15:
                raise Exception(f"Manual test job ID must be of form 'mYYYYMMDD_HHMMSS', got {date_str}")
            for i, c in enumerate(date_str):
                if i == 8 and c != "_" or i != 8 and not c.isdigit():
                    raise Exception(
                        f"Manual test job ID must be of form 'mYYYYMMDD_HHMMSS', got {date_str}"
                    )
        # Generate extra metadata to link mongo and minio
        metadata["job_id"] = job_id
        metadata["artifact_files"] = artifact_files
        metadata["hdl_hash"] = metadata["hdl_hash"].upper()
        metadata["linux_hash"] = metadata["linux_hash"].upper()
        metadata[
            "miniopath"
        ] = f"{self._minio_bucket}/{self._minio_subfolder}/{job_id}-h{metadata['hdl_hash']}-s{metadata['linux_hash']}"

        # DB checks
        self._check_mongo_and_minio()

        # Perform operations
        print(
            f"Inserting test data to MongoDB collection {self._mongo_database}/{self._mongo_collection}"
        )
        self.collection.insert_one(metadata)
        for file in artifact_files:
            target = f"{self._minio_subfolder}/{job_id}-h{metadata['hdl_hash']}-s{metadata['linux_hash']}/{os.path.basename(file)}"
            print(f"Uploading {file} to Minio bucket {self._minio_bucket} at {target}")
            self.minio.fput_object(self._minio_bucket, target, file)
