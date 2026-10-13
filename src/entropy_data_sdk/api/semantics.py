from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
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

    def list_namespaces(self) -> Page[SemanticNamespace]:
        return self._http.get_list(BASE, SemanticNamespace)

    def get_namespace(self, namespace: str) -> SemanticNamespace:
        return self._http.get_model(f"{BASE}/{seg(namespace)}", SemanticNamespace)

    def put_namespace(self, namespace: str, body: SemanticNamespace | dict[str, Any]) -> None:
        self._http.put_json(f"{BASE}/{seg(namespace)}", body)

    def delete_namespace(self, namespace: str) -> None:
        self._http.delete(f"{BASE}/{seg(namespace)}")

    def get_ontology_yaml(self, namespace: str) -> str:
        return self._http.get_text(f"{BASE}/{seg(namespace)}/ontology.yaml")

    def put_ontology_yaml(self, namespace: str, yaml_text: str, *, timeout: float | None = None) -> None:
        self._http.put_text(f"{BASE}/{seg(namespace)}/ontology.yaml", yaml_text, timeout=timeout)

    # Git connection

    def get_git_connection(self, namespace: str) -> GitConnectionResponse:
        return self._http.get_model(f"{BASE}/{seg(namespace)}/gitconnection", GitConnectionResponse)

    def put_git_connection(
        self, namespace: str, request: GitConnectionRequest | dict[str, Any]
    ) -> GitConnectionResponse:
        return self._http.put_model(f"{BASE}/{seg(namespace)}/gitconnection", request, GitConnectionResponse)

    def delete_git_connection(self, namespace: str) -> None:
        self._http.delete(f"{BASE}/{seg(namespace)}/gitconnection")

    def pull_from_git(self, namespace: str) -> GitConnectionResponse:
        return self._http.post_model(f"{BASE}/{seg(namespace)}/gitconnection/pull", GitConnectionResponse)

    def push_to_git(self, namespace: str, request: GitPushRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.post_model(f"{BASE}/{seg(namespace)}/gitconnection/push", GitConnectionResponse, request)

    def push_to_git_as_pull_request(
        self, namespace: str, request: GitPullRequestRequest | dict[str, Any]
    ) -> GitConnectionResponse:
        return self._http.post_model(f"{BASE}/{seg(namespace)}/gitconnection/push-pr", GitConnectionResponse, request)

    # Concepts and relationships

    def list_concepts(self, namespace: str) -> Page[SemanticConcept]:
        return self._http.get_list(f"{BASE}/{seg(namespace)}/concepts", SemanticConcept)

    def get_concept(self, namespace: str, concept: str) -> SemanticConcept:
        return self._http.get_model(f"{BASE}/{seg(namespace)}/concepts/{seg(concept)}", SemanticConcept)

    def put_concept(self, namespace: str, concept: str, body: SemanticConcept | dict[str, Any]) -> None:
        self._http.put_json(f"{BASE}/{seg(namespace)}/concepts/{seg(concept)}", body)

    def delete_concept(self, namespace: str, concept: str) -> None:
        self._http.delete(f"{BASE}/{seg(namespace)}/concepts/{seg(concept)}")

    def list_relationships(self, namespace: str) -> Page[SemanticRelationship]:
        return self._http.get_list(f"{BASE}/{seg(namespace)}/relationships", SemanticRelationship)

    def get_relationship(self, namespace: str, relationship: str) -> SemanticRelationship:
        return self._http.get_model(f"{BASE}/{seg(namespace)}/relationships/{seg(relationship)}", SemanticRelationship)

    def put_relationship(self, namespace: str, relationship: str, body: SemanticRelationship | dict[str, Any]) -> None:
        self._http.put_json(f"{BASE}/{seg(namespace)}/relationships/{seg(relationship)}", body)

    def delete_relationship(self, namespace: str, relationship: str) -> None:
        self._http.delete(f"{BASE}/{seg(namespace)}/relationships/{seg(relationship)}")

    # Branches

    def list_branches(self, namespace: str) -> Page[SemanticBranch]:
        return self._http.get_list(f"{BASE}/{seg(namespace)}/branches", SemanticBranch)

    def get_branch(self, namespace: str, branch: str) -> SemanticBranch:
        return self._http.get_model(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}", SemanticBranch)

    def create_branch(self, namespace: str, branch: str) -> SemanticBranch:
        return self._http.put_model(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}", {}, SemanticBranch)

    def delete_branch(self, namespace: str, branch: str) -> None:
        self._http.delete(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}")

    def rebase_branch(self, namespace: str, branch: str) -> SemanticBranch:
        return self._http.post_model(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}/rebase", SemanticBranch)

    def get_branch_ontology_yaml(self, namespace: str, branch: str) -> str:
        return self._http.get_text(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}/ontology.yaml")

    def put_branch_ontology_yaml(
        self, namespace: str, branch: str, yaml_text: str, *, timeout: float | None = None
    ) -> None:
        self._http.put_text(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}/ontology.yaml", yaml_text, timeout=timeout)

    def list_branch_changes(self, namespace: str, branch: str) -> Page[SemanticBranchChange]:
        return self._http.get_list(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}/changes", SemanticBranchChange)

    def merge_branch(self, namespace: str, branch: str) -> SemanticBranchMergeRequest | None:
        """Merge a branch. Returns the merge request when the namespace is git-connected, otherwise ``None``."""
        result = self._http.post_json(f"{BASE}/{seg(namespace)}/branches/{seg(branch)}/merge").data
        return SemanticBranchMergeRequest.model_validate(result) if result else None
