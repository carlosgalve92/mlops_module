from typing import Optional

from pydantic import BaseModel


# Esquema para la entrada de datos para la predicción
class PredictRequest(BaseModel):
    OCCUPATION: str
    AGE: float
    ANNUAL_INCOME: float
    NUM_OF_LOAN: float
    NUM_OF_DELAYED_PAYMENT: float
    CHANGED_CREDIT_LIMIT: float
    OUTSTANDING_DEBT: float
    AMOUNT_INVESTED_MONTHLY: float
    MONTHLY_BALANCE: float
    MONTHLY_INHAND_SALARY: float
    NUM_BANK_ACCOUNTS: float
    NUM_CREDIT_CARD: float
    INTEREST_RATE: float
    DELAY_FROM_DUE_DATE: float
    NUM_CREDIT_INQUIRIES: float
    CREDIT_UTILIZATION_RATIO: float
    TOTAL_EMI_PER_MONTH: float


# Esquema para la respuesta de predicción
class PredictResponse(BaseModel):
    prediction: float
    confidence: Optional[float] = None
