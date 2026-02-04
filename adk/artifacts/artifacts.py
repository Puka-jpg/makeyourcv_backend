from google.adk.artifacts import BaseArtifactService


class ArtifactService(BaseArtifactService):
    def __init__(self):
        pass
    
    def save_artifact(self, artifact: types.Artifact) -> types.Artifact:
        pass
    
    def get_artifact(self, artifact_id: str) -> types.Artifact:
        pass
    
    def delete_artifact(self, artifact_id: str) -> None:
        pass
    
    def get_artifact_version(self, artifact_id: str) -> types.ArtifactVersion:
        pass
    
    def get_artifact_versions(self, artifact_id: str) -> List[types.ArtifactVersion]:
        pass
