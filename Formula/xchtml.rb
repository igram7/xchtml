class Xchtml < Formula
  include Language::Python::Virtualenv

  desc "Generate beautiful HTML reports from Xcode .xcresult bundles"
  homepage "https://github.com/igram7/xchtml"
  url "https://github.com/igram7/xchtml/archive/refs/tags/v1.0.2.tar.gz"
  sha256 "db542246f024f385b046d474b3d6b08f8c90390e7880a3e5188e559e3a3876e0"
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
