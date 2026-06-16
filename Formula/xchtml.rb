class Xchtml < Formula
  include Language::Python::Virtualenv

  desc "Generate beautiful HTML reports from Xcode .xcresult bundles"
  homepage "https://github.com/igram7/xchtml"
  url "https://github.com/igram7/xchtml/archive/refs/tags/v1.0.3.tar.gz"
  sha256 "2e74e82af88ef45ecf35fa23d41d087e6bf8df4c86e2b19448faba6076e05ac0"
  license "MIT"

  depends_on "python@3.12"
  depends_on :macos

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "xchtml", shell_output("#{bin}/xchtml --version")
  end
end
