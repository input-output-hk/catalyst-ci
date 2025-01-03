"""This module provides a model for the /api/v0/vote/active/plans endpoint."""

# cspell: words pydantic

from typing import Optional

from pydantic import BaseModel, Field


class VotePlanProposalRangeOption(BaseModel):
    """Proposal range option.

    Attributes:
        start (int): The start of the range.
        end (int): The end of the range.
    """

    start: int
    end: int


class VotePlanProposalOptions(BaseModel):
    """Proposal options.

    Attributes:
        range (VotePlanProposalRangeOption): The proposal range.
    """

    range: VotePlanProposalRangeOption


class VotePlanProposalTallyResult(BaseModel):
    """Tally result.

    Attributes:
        results (list[int]): The results of the tally.
        options (VotePlanProposalOptions): The proposal options.
    """

    results: list[int]
    options: VotePlanProposalOptions


class VotePlanProposalTallyPrivateStateDecrypted(BaseModel):
    """Decrypted tally state.

    Attributes:
        result (VotePlanProposalTallyResult): Tally result.
    """

    result: VotePlanProposalTallyResult


class VotePlanProposalTallyPrivateStateEncrypted(BaseModel):
    """Encrypted tally state.

    Attributes:
        encrypted_tally (str): Encrypted tally.
        total_stake (int): Total stake.
    """

    encrypted_tally: str
    total_stake: Optional[int] = Field(default=None)


class VotePlanProposalTallyPrivateState(BaseModel):
    """Tally state.

    Attributes:
        encrypted (VotePlanProposalTallyPrivateStateEncrypted):
            Encrypted tally state.
        decrypted (VotePlanProposalTallyPrivateStateDecrypted):
            Decrypted tally state.
    """

    encrypted: Optional[VotePlanProposalTallyPrivateStateEncrypted] = Field(
        default=None, alias="Encrypted"
    )
    decrypted: Optional[VotePlanProposalTallyPrivateStateDecrypted] = Field(
        default=None, alias="Decrypted"
    )


class VotePlanProposalTallyPrivate(BaseModel):
    """Private tally result.

    Attributes:
        state (VotePlanProposalTallyPrivateState): Tally state.
    """

    state: VotePlanProposalTallyPrivateState


class VotePlanProposalTallyPublic(BaseModel):
    """Public tally result.

    Attributes:
        result (VotePlanProposalTallyResult): Tally result.
    """

    result: VotePlanProposalTallyResult


class VotePlanProposalTally(BaseModel):
    """Proposal tally.

    Attributes:
        public (VotePlanProposalTallyPublic): Public tally result.
        private (VotePlanProposalTallyPrivate): Private tally result.
    """

    public: Optional[VotePlanProposalTallyPublic] = Field(
        default=None, alias="Public"
    )
    private: Optional[VotePlanProposalTallyPrivate] = Field(
        default=None, alias="Private"
    )


class VotePlanProposal(BaseModel):
    """An active vote plan proposal.

    Attributes:
        index (int): Index of the proposal status.
        proposal_id (str): Hex-encoded proposal ID.
        options (VotePlanProposalRangeOption): The proposal options.
        tally (VotePlanProposalTally): Tally result.
        votes_cast (int): The number of votes cast for this proposal.
    """

    index: int
    proposal_id: str
    options: VotePlanProposalRangeOption
    tally: VotePlanProposalTally
    votes_cast: int


class VotePlan(BaseModel):
    """A vote plan.

    Attributes:
        id (str): Hex-encoded vote plan ID.
        payload (str): The type of payload to expect.
        vote_start (str): Epoch and slot ID of vote start time.
        vote_end (str): Epoch and slot ID of vote end time.
        committee_end (str): Epoch and slot ID of committee end time.
        committee_member_keys (list[str]): Committee member keys.
        proposals (list[VotePlanProposal]): Active proposals.
        voting_token (str): Voting token identifier.
    """

    id: str
    payload: str
    vote_start: str
    vote_end: str
    committee_end: str
    committee_member_keys: list[str]
    proposals: list[VotePlanProposal]
    voting_token: str
