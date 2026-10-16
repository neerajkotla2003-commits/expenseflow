from app.schemas import Category, PolicyRequest, PolicyResult

# Fictional company policy. Integer paise avoid floating-point money errors.
LIMITS_PAISE = {
    Category.MEAL: 100_000,         # Rs 1,000
    Category.TRAVEL: 500_000,       # Rs 5,000
    Category.EQUIPMENT: 2_000_000,  # Rs 20,000
}
FINANCE_THRESHOLD_PAISE = 1_000_000  # Above Rs 10,000


def evaluate_policy(expense: PolicyRequest) -> PolicyResult:
    if expense.amount_paise > LIMITS_PAISE[expense.category]:
        return PolicyResult(
            eligible=False,
            required_approver=None,
            reason="Amount exceeds the category limit.",
        )
    approver = (
        "finance"
        if expense.amount_paise > FINANCE_THRESHOLD_PAISE
        else "manager"
    )
    return PolicyResult(
        eligible=True,
        required_approver=approver,
        reason="Within policy; human approval is still required.",
    )
