from flask import url_for

from lib.tests import ViewTestMixin, assert_status_with_message


class TestInvoicesView(ViewTestMixin):
    def test_get_invoices(self, invoices):
        """
        User should see their billing history, even if they arn't currently
        subscribed.
        """
        self.authenticate()
        response = self.client.get(url_for('InvoicesView:index'))
        print(response.get_json())
        data = response.get_json()['data']
        invoice_history = data['invoices']

        assert response.status_code == 200
        assert data['upcoming_invoice'] is None
        assert len(invoice_history) == 2
