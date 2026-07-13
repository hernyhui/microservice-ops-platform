import httpx
from .config import settings


async def deduct_inventory(product_id: str, quantity: int) -> dict:
    url = f"{settings.inventory_service_url}/inventory/deduct"
    payload = {"product_id": product_id, "quantity": quantity}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = f"库存服务调用失败: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except Exception:
                pass
            raise Exception(error_detail)
        except httpx.RequestError as e:
            raise Exception(f"无法连接库存服务: {str(e)}")


async def get_inventory(product_id: str) -> dict:
    url = f"{settings.inventory_service_url}/inventory/{product_id}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"查询库存失败: {e.response.status_code}")
        except httpx.RequestError as e:
            raise Exception(f"无法连接库存服务: {str(e)}")
