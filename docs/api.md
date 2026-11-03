# CartPilot API quick reference

Base URL: `/api/v1/`

## Public
- `GET /health/`
- `POST /auth/register/`
- `POST /auth/token/`
- `POST /auth/token/refresh/`
- `GET /categories/`
- `GET /products/?search=lamp&category=1&min_price=100&max_price=2000&ordering=price`
- `GET /products/{id}/`
- `GET /products/{id}/price-history/`
- `GET /recommendations/`
- `GET /reviews/?product={id}`

## Authenticated
- `GET/PATCH /auth/me/`
- `GET/POST /cart/`
- `PATCH/DELETE /cart/items/{id}/`
- `GET/POST /wishlist/`
- `DELETE /wishlist/{id}/`
- `GET/POST/PATCH/DELETE /addresses/`
- `GET/POST/PATCH/DELETE /shopping-plans/`
- `POST /shopping-plans/{id}/items/`
- `DELETE /shopping-plans/{id}/items/{item_id}/`
- `POST /checkout/`
- `GET /orders/`, `GET /orders/{id}/`, `POST /orders/{id}/cancel/`
- `GET/POST/PATCH/DELETE /reviews/`
- `GET/POST/PATCH/DELETE /budgets/`
- `GET/POST/PATCH/DELETE /price-alerts/`
- `GET /insights/summary/`

## Staff-only
- Product/category write methods
- `GET /admin/analytics/`

Send JWTs using `Authorization: Bearer <access_token>`.
