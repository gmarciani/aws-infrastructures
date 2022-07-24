from aws_cdk import aws_budgets as budgets
from constructs import Construct


class SimpleBudget(budgets.CfnBudget):
    def __init__(self, scope: Construct, amount: float, threshold: float, email: str):
        super().__init__(
            scope,
            "BudgetDevWorkspace",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name="BudgetDevWorkspace",
                budget_type="COST",
                time_unit="MONTHLY",
                # the properties below are optional
                budget_limit=budgets.CfnBudget.SpendProperty(amount=amount, unit="USD"),
            ),
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        notification_type="ACTUAL",
                        comparison_operator="GREATER_THAN",
                        threshold=threshold,
                        threshold_type="PERCENTAGE",
                    ),
                    subscribers=[budgets.CfnBudget.SubscriberProperty(address=email, subscription_type="EMAIL")],
                )
            ],
        )
