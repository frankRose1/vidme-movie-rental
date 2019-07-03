from flask import url_for

from lib.tests import ViewTestMixin


class TestGetPlans(ViewTestMixin):
    def test_get_plans(self):
        """Should show a list of available plans to subscribe to"""
        response = self.client.get(url_for('PlansView:index'))
        plans = response.get_json()['data']['plans']
        assert response.status_code == 200

        assert plans['bronze']['id'] == 'bronze'
        assert plans['bronze']['amount'] == 499
        assert plans['bronze']['currency'] == 'usd'
        assert plans['bronze']['statement_descriptor'] == 'VIDME BRONZE'

        assert plans['gold']['id'] == 'gold'
        assert plans['gold']['amount'] == 999
        assert plans['gold']['currency'] == 'usd'
        assert plans['gold']['statement_descriptor'] == 'VIDME GOLD'

        assert plans['platinum']['id'] == 'platinum'
        assert plans['platinum']['amount'] == 1299
        assert plans['platinum']['currency'] == 'usd'
        assert plans['platinum']['statement_descriptor'] == 'VIDME PLATINUM'
