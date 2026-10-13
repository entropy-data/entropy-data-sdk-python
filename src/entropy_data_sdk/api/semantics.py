from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    GitConnectionRequest,
    GitConnectionResponse,
    GitPullRequestRequest,
    GitPushRequest,
    SemanticBranch,
    SemanticBranchChange,
    SemanticBranchMergeRequest,
    SemanticConcept,
    SemanticNamespace,
    SemanticRelationship,
)

BASE = "/api/semantics/experimental/namespaces"


class SemanticsApi(ApiGroup):
    """Semantic namespaces, concepts, relationships and branches. The API is marked experimental."""

    def list_namespaces(self) -> list[SemanticNamespace]:
        return self._http.get_list(BASE, SemanticNamespace)

    def get_namespace(self, namespace: str) -> SemanticNamespace:
        return self._http.get_model(f"{BASE}/{namespace}", SemanticNamespace)

    def put_namespace(self, namespace: str, body: SemanticNamespace | dict[str, Any]) -> None:
        self._http.put_json(f"{BASE}/{namespace}", body)

    def delete_namespace(self, namespace: str) -> None:
        self._http.delete(f"{BASE}/{namespace}")

    def get_ontology_yaml(self, namespace: str) -> str:
        return self._http.get_text(f"{BASE}/{namespace}/ontology.yaml")

    def put_ontology_yaml(self, namespace: str, yaml_text: str, *, timeout: float | None = None) -> None:
        self._http.request(
            "PUT",
            f"{BASE}/{namespace}/ontology.yaml",
            content=yaml_text,
            content_type="application/yaml",
            timeout=timeout,
        )

    # Git connection

    def get_git_connection(self, namespace: str) -> GitConnectionResponse:
        return self._http.get_model(f"{BASE}/{namespace}/gitconnection", GitConnectionResponse)

    def put_git_connection(
        self, namespace: str, request: GitConnectionRequest | dict[str, Any]
    ) -> GitConnectionResponse:
        return self._http.put_model(f"{BASE}/{namespace}/gitconnection", request, GitConnectionResponse)

    def delete_git_connection(self, namespace: str) -> None:
        self._http.delete(f"{BASE}/{namespace}/gitconnection")

    def pull_from_git(self, namespace: str) -> GitConnectionResponse:
        return self._http.post_model(f"{BASE}/{namespace}/gitconnection/pull", GitConnectionResponse)

    def push_to_git(self, namespace: str, request: GitPushRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.post_model(f"{BASE}/{namespace}/gitconnection/push", GitConnectionResponse, request)

    def push_to_git_as_pull_request(
        self, namespace: str, request: GitPullRequestRequest | dict[str, Any]
    ) -> GitConnectionResponse:
        return self._http.post_model(f"{BASE}/{namespace}/gitconnection/push-pr", GitConnectionResponse, request)

    # Concepts and relationships

    def list_concepts(self, namespace: str) -> list[SemanticConcept]:
        return self._http.get_list(f"{BASE}/{namespace}/concepts", SemanticConcept)

    def get_concept(self, namespace: str, concept: str) -> SemanticConcept:
        return self._http.get_model(f"{BASE}/{namespace}/concepts/{concept}", SemanticConcept)

    def put_concept(self, namespace: str, concept: str, body: SemanticConcept | dict[str, Any]) -> None:
        self._http.put_json(f"{BASE}/{namespace}/concepts/{concept}", body)

    def delete_concept(self, namespace: str, concept: str) -> None:
        self._http.delete(f"{BASE}/{namespace}/concepts/{concept}")

    def list_relationships(self, namespace: str) -> list[SemanticRelationship]:
        return self._http.get_list(f"{BASE}/{namespace}/relationships", SemanticRelationship)

    def get_relationship(self, namespace: str, relationship: str) -> SemanticRelationship:
        return self._http.get_model(f"{BASE}/{namespace}/relationships/{relationship}", SemanticRelationship)

    def put_relationship(self, namespace: str, relationship: str, body: SemanticRelationship | dict[str, Any]) -> None:
        self._http.put_json(f"{BASE}/{namespace}/relationships/{relationship}", body)

    def delete_relationship(self, namespace: str, relationship: str) -> None:
        self._http.delete(f"{BASE}/{namespace}/relationships/{relationship}")

    # Branches

    def list_branches(self, namespace: str) -> list[SemanticBranch]:
        return self._http.get_list(f"{BASE}/{namespace}/branches", SemanticBranch)

    def get_branch(self, namespace: str, branch: str) -> SemanticBranch:
        return self._http.get_model(f"{BASE}/{namespace}/branches/{branch}", SemanticBranch)

    def create_branch(self, namespace: str, branch: str) -> SemanticBranch:
        return self._http.put_model(f"{BASE}/{namespace}/branches/{branch}", {}, SemanticBranch)

    def delete_branch(self, namespace: str, branch: str) -> None:
        self._http.delete(f"{BASE}/{namespace}/branches/{branch}")

    def rebase_branch(self, namespace: str, branch: str) -> SemanticBranch:
        return self._http.post_model(f"{BASE}/{namespace}/branches/{branch}/rebase", SemanticBranch)

    def get_branch_ontology_yaml(self, namespace: str, branch: str) -> str:
        return self._http.get_text(f"{BASE}/{namespace}/branches/{branch}/ontology.yaml")

    def put_branch_ontology_yaml(
        self, namespace: str, branch: str, yaml_text: str, *, timeout: float | None = None
    ) -> None:
        self._http.request(
            "PUT",
            f"{BASE}/{namespace}/branches/{branch}/ontology.yaml",
            content=yaml_text,
            content_type="application/yaml",
            timeout=timeout,
        )

    def list_branch_changes(self, namespace: str, branch: str) -> list[SemanticBranchChange]:
        return self._http.get_list(f"{BASE}/{namespace}/branches/{branch}/changes", SemanticBranchChange)

    def merge_branch(self, namespace: str, branch: str) -> SemanticBranchMergeRequest | None:
        """Merge a branch. Returns the merge request when the namespace is git-connected, otherwise ``None``."""
        result = self._http.post_json(f"{BASE}/{namespace}/branches/{branch}/merge")
        return SemanticBranchMergeRequest.model_validate(result) if result else None
