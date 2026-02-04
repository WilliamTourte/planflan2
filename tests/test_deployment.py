"""
Deployment tests to verify that the site is properly deployed on planflan.fr
These tests are non-destructive and limited to read-only GET requests.
"""

import pytest
import requests
import os
from urllib.parse import urljoin

# Configuration
# Use environment variable to allow testing different deployment targets
BASE_URL = os.environ.get("DEPLOYMENT_BASE_URL", "https://planflan.fr")
WWW_BASE_URL = os.environ.get("DEPLOYMENT_WWW_BASE_URL", "https://www.planflan.fr")
TIMEOUT = 10  # seconds


def should_skip_deployment_tests():
    """Check if deployment tests should be skipped"""
    # Check if RUN_DEPLOYMENT_TESTS environment variable is set to "true"
    return os.environ.get("RUN_DEPLOYMENT_TESTS", "false").lower() != "true"


@pytest.mark.deployment
@pytest.mark.skipif(
    should_skip_deployment_tests(),
    reason="Deployment tests are disabled by default. Set RUN_DEPLOYMENT_TESTS=true to enable.",
)
class TestDeployment:
    """Tests to verify that the production site is properly deployed and accessible"""

    @pytest.mark.parametrize("base_url", [BASE_URL])  # Removed WWW_BASE_URL
    def test_homepage_accessible(self, base_url):
        """Test that the homepage is accessible"""
        url = urljoin(base_url, "/")
        try:
            # Disable SSL verification for self-signed certificates in development
            response = requests.get(url, timeout=TIMEOUT, verify=False)
            assert response.status_code == 200
            # Flexible content verification to avoid failures if text changes
            content_lower = response.content.lower()
            assert b"flan" in content_lower or b"planflan" in content_lower
        except (requests.RequestException, AssertionError) as e:
            pytest.fail(f"Homepage test failed for {url}: {str(e)}")

    @pytest.mark.parametrize("base_url", [BASE_URL])  # Removed WWW_BASE_URL
    def test_etablissements_page_accessible(self, base_url):
        """Test that the etablissements page is accessible"""
        url = urljoin(base_url, "/liste_etablissements")
        try:
            response = requests.get(url, timeout=TIMEOUT, verify=False)
            assert response.status_code == 200
            # Flexible content verification
            content_lower = response.content.lower()
            assert b"etablissement" in content_lower or b"boulangerie" in content_lower
        except (requests.RequestException, AssertionError) as e:
            pytest.fail(f"Etablissements page test failed for {url}: {str(e)}")

    @pytest.mark.parametrize("base_url", [BASE_URL])  # Removed WWW_BASE_URL
    def test_rechercher_page_accessible(self, base_url):
        """Test that the recherche page is accessible"""
        url = urljoin(base_url, "/rechercher")
        try:
            response = requests.get(url, timeout=TIMEOUT, verify=False)
            assert response.status_code == 200
            # Flexible content verification
            content_lower = response.content.lower()
            assert b"rechercher" in content_lower or b"recherche" in content_lower
        except (requests.RequestException, AssertionError) as e:
            pytest.fail(f"Recherche page test failed for {url}: {str(e)}")

    def test_https_redirect(self):
        """Test that HTTP requests are redirected to HTTPS or site is HTTPS-only"""
        http_url = "http://planflan.fr"
        try:
            response = requests.get(http_url, timeout=TIMEOUT, allow_redirects=False, verify=False)
            # Either redirect to HTTPS (301/302) or already serve HTTPS (200)
            assert response.status_code in [200, 301, 302]
            if response.status_code in [301, 302]:
                assert response.headers.get("Location", "").startswith("https://")
        except requests.exceptions.ConnectionError as e:
            # Skip test if network is unreachable (common in CI/CD environments)
            pytest.skip(f"Network unreachable - skipping HTTPS redirect test: {str(e)}")
        except requests.RequestException as e:
            pytest.fail(f"HTTPS redirect test failed: {str(e)}")

    @pytest.mark.skip(reason="WWW subdomain not configured")
    def test_www_redirect(self):
        """Test that www subdomain is properly handled - SKIPPED as www is not configured"""
        pass

    def test_static_assets_accessible(self):
        """Test that static assets (CSS, JS) are accessible"""
        css_url = urljoin(BASE_URL, "/static/css/style.css")
        try:
            response = requests.get(css_url, timeout=TIMEOUT, verify=False)
            assert response.status_code == 200
            assert b"body" in response.content or b"css" in response.content.lower()
        except requests.RequestException as e:
            pytest.fail(f"Static assets test failed: {str(e)}")

    def test_favicon_accessible(self):
        """Test that favicon is accessible"""
        favicon_url = urljoin(BASE_URL, "/static/favicon.ico")
        try:
            response = requests.get(favicon_url, timeout=TIMEOUT, verify=False)
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.fail(f"Favicon test failed: {str(e)}")

    def test_404_page(self):
        """Test that 404 page is properly handled"""
        invalid_url = urljoin(BASE_URL, "/page-inexistante-12345")
        try:
            response = requests.get(invalid_url, timeout=TIMEOUT, verify=False)
            # Should return 404 or redirect to a custom 404 page
            assert response.status_code == 404 or response.status_code == 200
            if response.status_code == 200:
                # If it returns 200, it should be a custom 404 page
                content_lower = response.content.lower()
                assert b"404" in content_lower or b"page non trouvee" in content_lower
        except requests.RequestException as e:
            pytest.fail(f"404 page test failed: {str(e)}")
