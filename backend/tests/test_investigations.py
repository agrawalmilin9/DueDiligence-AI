def test_list_investigations(client):
    response = client.get("/investigations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check camelCase fields matching frontend TypeScript InvestigationSummary
    first = data[0]
    assert "id" in first
    assert "companyName" in first
    assert "sector" in first
    assert "request" in first
    assert "verdict" in first
    assert "score" in first


def test_create_investigation_sync(client):
    payload = {
        "companyName": "Apex BioTech",
        "request": "Analyze for a $3M Series A co-investment.",
    }
    response = client.post("/investigations?sync=true", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["companyName"] == "Apex BioTech"
    assert data["status"] == "completed"
    assert data["currentStep"] == "completed"
    assert "id" in data
    assert "report" in data
    assert data["report"] is not None

    report = data["report"]
    # Check camelCase contract matching TypeScript InvestigationReport
    assert "generatedAt" in report
    assert report["company"]["name"] == "Apex BioTech"
    assert "businessModel" in report["company"]
    assert "totalFunding" in report["metrics"]
    assert "lastRound" in report["metrics"]
    assert "employeeGrowth" in report["metrics"]
    assert isinstance(report["founders"], list)
    assert isinstance(report["competitors"], list)
    assert isinstance(report["findings"], list)
    assert isinstance(report["risks"], list)
    assert isinstance(report["claims"], list)
    assert "verdict" in report["recommendation"]
    assert "thesis" in report["memo"]


def test_create_investigation_with_company_alias(client):
    # Frontend form sends 'company' field name
    payload = {
        "company": "Neural Flow Systems",
        "request": "Check customer traction claims.",
    }
    response = client.post("/investigations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["companyName"] == "Neural Flow Systems"
    assert data["status"] == "completed"


def test_create_investigation_empty_name_fails(client):
    response = client.post("/investigations", json={"companyName": "   "})
    assert response.status_code == 422


def test_get_investigation_by_id(client):
    response = client.get("/investigations/vectrix-robotics")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "vectrix-robotics"
    assert data["companyName"] == "Vectrix Robotics"
    assert data["status"] == "completed"
    assert data["report"] is not None


def test_get_investigation_not_found(client):
    response = client.get("/investigations/non-existent-startup-id-999")
    assert response.status_code == 404


def test_get_investigation_direct_report(client):
    response = client.get("/investigations/lumora-health/report")
    assert response.status_code == 200
    report = response.json()

    # Exact 1:1 match with frontend InvestigationReport
    assert report["id"] == "lumora-health"
    assert report["company"]["name"] == "Lumora Health"
    assert "businessModel" in report["company"]
    assert "totalFunding" in report["metrics"]
    assert "lastRound" in report["metrics"]
    assert "employeeGrowth" in report["metrics"]
    assert report["recommendation"]["verdict"] in ["PROCEED", "PROCEED_WITH_CAUTION", "AVOID"]
    assert isinstance(report["recommendation"]["score"], (int, float))
    assert isinstance(report["recommendation"]["conditions"], list)
    assert "thesis" in report["memo"]
    assert "sections" in report["memo"]


def test_create_investigation_async_status_tracking(client):
    payload = {
        "companyName": "Async Robotics Labs",
        "request": "Evaluate hardware pipeline.",
    }
    # With sync=false, it enqueues into background_tasks and immediately returns pending/running
    response = client.post("/investigations?sync=false", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["companyName"] == "Async Robotics Labs"
    assert data["status"] in ["pending", "running", "completed"]
