from streamlit.testing.v1 import AppTest


def test_app_mock_mode():
    # Set query parameters to mock=true
    at = AppTest.from_file("frontend/streamlit_app.py", default_timeout=30)
    at.query_params["mock"] = "true"

    # Run the app
    at.run()

    # Click run button
    run_btn = at.button[0]
    assert run_btn.label == "🚀 Run Analysis"

    run_btn.click().run()

    # Verify intermediate status box exists
    assert len(at.status) > 0
    status_box = at.status[0]
    assert status_box.label == "Analysis complete!"

    # Verify the output/response is displayed
    markdown_texts = [m.value for m in at.markdown]
    print("Markdown texts:")
    for txt in markdown_texts:
        print(f"- {txt}")

    assert any("Based on Section 3.3" in txt for txt in markdown_texts)
