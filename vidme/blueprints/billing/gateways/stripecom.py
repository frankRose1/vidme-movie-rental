import stripe


class Subscription(object):
    @classmethod
    def create(cls, token=None, email=None, plan=None):
        """
        Send a request to the stripe API to create a new subscription.

        :param email: User's email
        :type email: str
        :param plan: Plan to subscribe to
        :type plan: str
        :param token: One-time use token provided by stripe
        :type token: str

        :return: Stripe customer
        """
        params = {
            'source': token,
            'email': email,
            'plan': plan
        }

        return stripe.Customer.create(**params)

    @classmethod
    def update(cls, customer_id=None, plan=None):
        """
        Send a request to the stripe API to update an existing subscription
        without interupting the users access to our platform or requiring the
        user to re-enter their billing info.

        :param customer_id: User's payment ID. initally set when user
        subscribes on our platform
        :type customer_id: str

        :param plan: New plan to subscribe to
        :type plan: str

        :return: Stripe subscription object
        """
        customer = stripe.Customer.retrieve(customer_id)
        subscription_id = customer.subscriptions.data[0].id
        subscription = customer.subscriptions.retrieve(subscription_id)
        # change the old plan to the new one Stripe
        subscription.plan = plan
        return subscription.save()

    @classmethod
    def cancel(cls, customer_id=None):
        """
        Send a request to the stripe API to cancel a user's subscription.

        :param customer_id: User's payment ID. initally set when user
        subscribes on our platform
        :type customer_id: str

        :return: Stripe subscription object
        """
        customer = stripe.Customer.retrieve(customer_id)
        subscription_id = customer.subscriptions.data[0].id

        return customer.subscriptions.retrieve(subscription_id).delete()


class Card(object):
    @classmethod
    def update(cls, customer_id, stripe_token=None):
        """
        Update an existing card through a customer.
        API docs: https://stripe.com/docs/api/python#update_card

        :param: customer_id: Stripe customer id
        :type customer_id: int
        :param stripe_token: Stripe token
        :type stripe_token: str
        :return: Stripe customer
        """
        customer = stripe.Customer.retrieve(customer_id)
        # uses the new token to update the billing info
        # will not effect the subscription at all
        customer.source = stripe_token
        return customer.save()


class Product(object):

    @classmethod
    def retrieve(cls, product):
        """
        Retrieve an existing product.
        API docs: https://stripe.com/docs/api#retrieve_product

        :param product: Product identifier
        :type product: str

        :return: Stripe product
        """
        try:
            return stripe.Product.retrieve(product)
        except stripe.error.StripeError as e:
            print(e)


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

            plan.nickname = name
            plan.metadata = metadata
            product_id = plan.product
            updated_plan = plan.save()

            product = Product.retrieve(product_id)
            product.name = name
            product.statement_descriptor = statement_descriptor

            return updated_plan
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
            # must delete plan before deleting a product
            plan = stripe.Plan.retrieve(plan)
            product_id = plan.product
            deleted_plan = plan.delete()

            product = Product.retrieve(product_id)
            product.delete()

            return deleted_plan
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
            # newer versions of stripes API require a Prouct associated
            # with a plan
            product = {
                'name': name,
                'statement_descriptor': statement_descriptor
            }

            return stripe.Plan.create(id=id,
                                      nickname=name,
                                      amount=amount,
                                      currency=currency,
                                      interval=interval,
                                      interval_count=interval_count,
                                      trial_period_days=trial_period_days,
                                      metadata=metadata,
                                      product=product
                                      )
        except stripe.error.StripeError as e:
            print(e)
