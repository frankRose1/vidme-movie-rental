import stripe


class Plan(object):
    """
    Plan class provides a means of interacting with the stripe API and will
    perform tasks such as creating, listing, deleting, and updating plans for
    the application. Used heavily in the CLI.
    """
    @classmethod
    def retrieve(cls, plan):
        """
        Retrieve an existing plan.
        API docs: https://stripe.com/docs/api#retrieve_plan

        :param plan: Plan identifier
        :type plan: str
        :return: Stripe plan
        """
        try:
            return stripe.Plan.retrieve(plan)
        except stripe.error.StripeError as e:
            print(e)

        @classmethod
        def list(cls):
            """
            List all plans.
            API docs: https://stripe.com/docs/api#list_plans

            :return: Stripe plans
            """
            try:
                return stripe.Plan.all()
            except stripe.error.StripeError as e:
                print(e)

        @classmethod
        def update(cls, id=None, name=None, metadata=None,
                   statement_descriptor=None):
            """
            Update an existing plan.

            API docs: https://stripe.com/docs/api#update_plan

            :param id: Plan identifier
            :param name: Plan name
            :param metadata: Additional data regarding the plan
            :statement_descriptor: String to appear on CC statement

            :return: Stripe plan
            """
            try:
                plan = stripe.Plan.retrieve(id)

                plan.name = name
                plan.metadata = metadata
                plan.statement_descriptor = statement_descriptor
                return plan.save()
            except stripe.error.StripeError as e:
                print(e)

        @classmethod
        def delete(cls, plan):
            """
            Delete an existing plan.

            API docs: https://stripe.com/docs/api#delete_plan

            :param plan: Plan identifier
            :type plan: str
            :return: Stripe plan object
            """
            try:
                plan = stripe.Plan.retrieve(plan)
                return plan.delete()
            except stripe.error.StripeError as e:
                print(e)

    @classmethod
    def create(cls, id=None, name=None, amount=None, currency=None,
               interval=None, interval_count=None, trial_period_days=None,
               metadata=None, statement_descriptor=None):
        """
        Create a new plan.

        API docs: https://stripe.com/docs/api#create_plan

        :param id: Plan identifier
        :type id: str
        :param name: Plan name
        :type name: str
        :param amount: Amount in cents to charge or 0 for a free plan
        :type amount: int
        :param currency: 3 digit currency abbreviation
        :type currency: str
        :param interval: Billing frequency
        :type interval: str
        :param interval_count: Number of intervals between each bill
        :type interval_count: int
        :param trial_period_days: Number of days to run a free trial
        :type trial_period_days: int
        :param metadata: Additional data to save with the plan
        :type metadata: dct
        :param statement_descriptor: String to appear on CC statement
        :type statement_descriptor: str
        :return: Stripe plan
        """
        try:
            return stripe.Plan.create(id=id,
                                      name=name,
                                      amount=amount,
                                      currency=currency,
                                      interval=interval,
                                      interval_count=interval_count,
                                      trial_period_days=trial_period_days,
                                      metadata=metadata,
                                      statement_descriptor=statement_descriptor
                                      )
        except stripe.error.StripeError as e:
            print(e)
