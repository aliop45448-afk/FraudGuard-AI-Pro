# FraudGuard AI Pro - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:5000/api/v1`  
**Authentication:** JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Transactions](#transactions)
3. [Dashboards](#dashboards)
4. [Models](#models)
5. [Webhooks](#webhooks)
6. [Banking Integration](#banking-integration)
7. [Reports](#reports)
8. [Cases](#cases)
9. [Security](#security)
10. [AI Assistant](#ai-assistant)
11. [Integrations](#integrations)
12. [Error Handling](#error-handling)

---

## Authentication

### Register User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "User Name"
}
```

**Response:**
```json
{
  "user_id": "user_001",
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2024-01-20T10:30:00Z"
}
```

### Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_value",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### Verify MFA

**Endpoint:** `POST /auth/mfa/verify`

**Request:**
```json
{
  "user_id": "user_001",
  "mfa_code": "123456"
}
```

**Response:**
```json
{
  "verified": true,
  "message": "MFA verification successful"
}
```

---

## Transactions

### Detect Fraud

**Endpoint:** `POST /transactions/detect`

**Request:**
```json
{
  "transaction_id": "txn_123",
  "transaction_amount": 1500.00,
  "merchant_id": "merchant_001",
  "merchant_category": "Electronics",
  "user_id": "user_001",
  "user_location": "New York, USA",
  "transaction_time": "2024-01-20T10:30:00Z",
  "device_fingerprint": "device_abc123",
  "ip_address": "192.168.1.1",
  "card_last_four": "4242"
}
```

**Response:**
```json
{
  "transaction_id": "txn_123",
  "fraud_probability": 0.15,
  "risk_score": 35.5,
  "is_flagged": false,
  "confidence": 0.92,
  "recommendation": "APPROVE",
  "processing_time_ms": 125,
  "timestamp": "2024-01-20T10:30:00Z",
  "model_predictions": {
    "rf_v1": 0.12,
    "gb_v1": 0.18,
    "if_v1": 0.15
  }
}
```

### Batch Detect Fraud

**Endpoint:** `POST /transactions/batch-detect`

**Request:**
```json
{
  "transactions": [
    { "transaction_id": "txn_001", ... },
    { "transaction_id": "txn_002", ... }
  ]
}
```

**Response:**
```json
{
  "total_transactions": 2,
  "processed": 2,
  "results": [
    {
      "transaction_id": "txn_001",
      "fraud_probability": 0.15,
      "risk_score": 35.5,
      "is_flagged": false,
      "recommendation": "APPROVE"
    }
  ]
}
```

### Get Transaction

**Endpoint:** `GET /transactions/{transaction_id}`

**Response:**
```json
{
  "transaction_id": "txn_123",
  "amount": 1500.00,
  "merchant_id": "merchant_001",
  "user_id": "user_001",
  "fraud_probability": 0.15,
  "risk_score": 35.5,
  "status": "approved",
  "created_at": "2024-01-20T10:30:00Z"
}
```

---

## Dashboards

### Get Dashboard Metrics

**Endpoint:** `GET /dashboards/metrics`

**Response:**
```json
{
  "current_snapshot": {
    "total_transactions": 1000,
    "fraudulent_transactions": 50,
    "fraud_rate": 0.05,
    "average_risk_score": 35.5,
    "blocked_transactions": 25,
    "timestamp": "2024-01-20T10:30:00Z"
  },
  "model_performance": {
    "rf_v1": {
      "average_fraud_probability": 0.45,
      "predictions_count": 1250
    }
  },
  "geographic_distribution": {
    "USA": 30,
    "Canada": 10,
    "UK": 10
  }
}
```

### Get Fraud Timeline

**Endpoint:** `GET /dashboards/fraud-timeline?period=24h`

**Response:**
```json
{
  "timeline": [
    {
      "timestamp": "2024-01-20T10:00:00Z",
      "fraud_count": 5,
      "transaction_count": 100
    }
  ]
}
```

---

## Models

### List Models

**Endpoint:** `GET /models`

**Response:**
```json
{
  "total_models": 5,
  "models": [
    {
      "model_id": "rf_v1",
      "model_type": "random_forest",
      "version": "1.0",
      "accuracy": 0.94,
      "precision": 0.92,
      "recall": 0.94,
      "f1_score": 0.93,
      "is_active": true,
      "last_trained": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### Get Model Details

**Endpoint:** `GET /models/{model_id}`

**Response:**
```json
{
  "model_id": "rf_v1",
  "model_type": "random_forest",
  "version": "1.0",
  "accuracy": 0.94,
  "precision": 0.92,
  "recall": 0.94,
  "f1_score": 0.93,
  "is_active": true,
  "last_trained": "2024-01-20T10:30:00Z"
}
```

### Activate Model

**Endpoint:** `POST /models/{model_id}/activate`

**Response:**
```json
{
  "model_id": "rf_v1",
  "status": "activated"
}
```

---

## Webhooks

### Create Webhook

**Endpoint:** `POST /webhooks`

**Request:**
```json
{
  "event_type": "fraud_detected",
  "url": "https://example.com/webhook"
}
```

**Response:**
```json
{
  "webhook_id": "webhook_001",
  "event_type": "fraud_detected",
  "url": "https://example.com/webhook",
  "status": "active",
  "created_at": "2024-01-20T10:30:00Z"
}
```

### List Webhooks

**Endpoint:** `GET /webhooks`

**Response:**
```json
{
  "total": 3,
  "webhooks": [
    {
      "webhook_id": "webhook_001",
      "event_type": "fraud_detected",
      "url": "https://example.com/webhook",
      "status": "active"
    }
  ]
}
```

### Delete Webhook

**Endpoint:** `DELETE /webhooks/{webhook_id}`

**Response:**
```json
{
  "webhook_id": "webhook_001",
  "status": "deleted"
}
```

---

## Banking Integration

### Add Banking Integration

**Endpoint:** `POST /banking/integrations`

**Request:**
```json
{
  "bank_name": "Example Bank",
  "api_key": "your-api-key",
  "endpoint": "https://api.bank.com"
}
```

**Response:**
```json
{
  "integration_id": "bank_001",
  "bank_name": "Example Bank",
  "status": "active"
}
```

### Sync Transactions

**Endpoint:** `POST /banking/integrations/{integration_id}/sync`

**Response:**
```json
{
  "status": "success",
  "bank": "Example Bank",
  "transactions_synced": 150,
  "last_sync": "2024-01-20T10:30:00Z"
}
```

---

## Reports

### Generate Report

**Endpoint:** `POST /reports/generate`

**Request:**
```json
{
  "report_type": "daily",
  "period_start": "2024-01-20T00:00:00Z",
  "period_end": "2024-01-20T23:59:59Z"
}
```

**Response:**
```json
{
  "report_id": "report_001",
  "report_type": "daily",
  "total_transactions": 1000,
  "fraudulent_transactions": 50,
  "fraud_rate": 0.05,
  "average_risk_score": 35.5,
  "blocked_transactions": 25,
  "created_at": "2024-01-20T10:30:00Z"
}
```

### List Reports

**Endpoint:** `GET /reports?type=daily`

**Response:**
```json
{
  "total": 5,
  "reports": [
    {
      "report_id": "report_001",
      "report_type": "daily",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

---

## Cases

### Create Case

**Endpoint:** `POST /cases`

**Request:**
```json
{
  "transaction_id": "txn_123",
  "priority": "high",
  "description": "Suspicious transaction pattern detected",
  "evidence": {
    "velocity": "high",
    "geographic_anomaly": true
  }
}
```

**Response:**
```json
{
  "case_id": "case_001",
  "transaction_id": "txn_123",
  "status": "open",
  "priority": "high",
  "created_at": "2024-01-20T10:30:00Z"
}
```

### Update Case

**Endpoint:** `PUT /cases/{case_id}`

**Request:**
```json
{
  "status": "resolved",
  "assigned_to": "investigator_001",
  "resolution_notes": "Case resolved after investigation"
}
```

**Response:**
```json
{
  "case_id": "case_001",
  "status": "resolved",
  "assigned_to": "investigator_001",
  "updated_at": "2024-01-20T11:30:00Z"
}
```

---

## Security

### Encrypt Data

**Endpoint:** `POST /security/encrypt`

**Request:**
```json
{
  "data": "sensitive_information"
}
```

**Response:**
```json
{
  "encrypted": "encrypted_data_hash",
  "key_id": "key_001",
  "algorithm": "AES-256-Fernet"
}
```

### Decrypt Data

**Endpoint:** `POST /security/decrypt`

**Request:**
```json
{
  "encrypted": "encrypted_data_hash"
}
```

**Response:**
```json
{
  "decrypted": "sensitive_information",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Audit Log

**Endpoint:** `POST /security/audit/log`

**Request:**
```json
{
  "user_id": "user_001",
  "action": "CREATE",
  "resource_type": "transaction",
  "resource_id": "txn_123"
}
```

**Response:**
```json
{
  "log_id": "audit_001",
  "user_id": "user_001",
  "action": "CREATE",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## AI Assistant

### Query Assistant

**Endpoint:** `POST /assistant/query`

**Request:**
```json
{
  "query": "What is the current fraud rate?"
}
```

**Response:**
```json
{
  "response_id": "resp_001",
  "query": "What is the current fraud rate?",
  "response_text": "The current fraud rate is 5%",
  "confidence_score": 0.92,
  "recommendations": [
    "Increase monitoring for high-risk merchants"
  ]
}
```

### Detect Fraud Patterns

**Endpoint:** `POST /patterns/detect`

**Request:**
```json
{
  "transactions": [
    { "transaction_id": "txn_001", ... }
  ]
}
```

**Response:**
```json
{
  "total": 1,
  "patterns": [
    {
      "pattern_id": "pattern_001",
      "pattern_type": "velocity_abuse",
      "frequency": 15,
      "risk_level": "high"
    }
  ]
}
```

### Run Simulation

**Endpoint:** `POST /simulation/run`

**Request:**
```json
{
  "scenario_name": "High-value transactions",
  "transaction_count": 1000,
  "fraud_percentage": 0.05
}
```

**Response:**
```json
{
  "simulation_id": "sim_001",
  "scenario_name": "High-value transactions",
  "transaction_count": 1000,
  "detected_frauds": 47,
  "detection_rate": 0.94,
  "model_performance": {
    "precision": 0.92,
    "recall": 0.94,
    "f1_score": 0.93
  }
}
```

---

## Integrations

### Add Integration

**Endpoint:** `POST /integrations`

**Request:**
```json
{
  "name": "SIEM Integration",
  "type": "siem",
  "config": {
    "endpoint": "https://siem.example.com",
    "api_key": "your-api-key"
  }
}
```

**Response:**
```json
{
  "integration_id": "int_001",
  "name": "SIEM Integration",
  "type": "siem",
  "status": "active",
  "created_at": "2024-01-20T10:30:00Z"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "error_code": "INVALID_REQUEST",
  "status_code": 400,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

### Common Error Codes

| Code | Description |
|------|-------------|
| INVALID_REQUEST | Invalid request parameters |
| UNAUTHORIZED | Missing or invalid authentication |
| FORBIDDEN | Insufficient permissions |
| NOT_FOUND | Resource not found |
| INTERNAL_ERROR | Server error |

---

## Rate Limiting

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642683600
```

**Rate Limits:**
- 1,000 requests per hour per user
- 10,000 requests per hour per API key

---

## Pagination

**Query Parameters:**
```
GET /transactions?page=1&limit=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

**API Version:** 1.0.0  
**Last Updated:** January 20, 2024
