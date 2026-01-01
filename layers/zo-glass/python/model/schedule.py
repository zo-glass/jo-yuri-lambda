from .base import Base
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class Schedule(Base):
    PARTITION = "schedule"

    REQUIRED_KEYS = ["href", "title", "start"]
    OPTIONAL_KEYS = ["subtitle", "end", "allDay"]
    EDITABLE_KEYS = ["href", "title", "subtitle", "end", "allDay"]
    URL_KEYS = ["href"]

    def get_handler(self, queryStringParameters=None, full=False):
        data = {
            "items": [],
            "pageInfo": {},
            "nextPageToken": ""
        }
        start = queryStringParameters.get("start")
        end = queryStringParameters.get("end")
        tz = queryStringParameters.get("timezone")

        try:
            tz = ZoneInfo(tz) if tz else timezone.utc
        except Exception:
            return 400, {"statusDescription": "Invalid timezone"}

        start = self.parse_to_utc(start, tz)
        end = self.parse_to_utc(end, tz)

        if not start or not end:
            return 400, {"statusDescription": "Invalid or missing start and/or end parameters"}

        res = self.db.get_by_range_handler(self.PARTITION, start, end)
        
        items = res.get("items")
        lek = res.get("lastEvaluatedKey")

        data.update(self.format_items(items, full=full))

        if lek:
            data["nextPageToken"] = self.lekToToken(lek)

        data["pageInfo"]["resultsPerPage"] = len(items)
        data["pageInfo"]["totalResults"] = self.db.getCountByRange(self.PARTITION, start, end)
        
        return 200, data
        
    def parse_to_utc(self, date, tz):
        try:
            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            return None
    
    def post_handler(self, data, user, ttl=None):
        item = {
            "PK": self.PARTITION,
            "createdAt": int(time.time()),
            "createdBy": user
        }

        missingKeys = self.requiredKeysValidator(data)
        if missingKeys:
            return 400, {"errorDescription": f"Missing {", ".join(missingKeys)} key"}
        
        invalid_urls = self.invalidUrlValidator(data)
        if invalid_urls:
            return 400, {"errorDescription": f"{", ".join(invalid_urls)} invalid URLs"}
        
        lastId = self.db.getNextSK(self.PARTITION)
        item["id"] = f"ITEM#{data["start"]}_{lastId}"

        if ttl is not None:
            item["ttl"] = ttl

        for key in self.REQUIRED_KEYS + self.OPTIONAL_KEYS + self.AUXILIARY_KEYS:
                if key in data:
                    item[key] = data[key]

        try:
            self.db.post_handler(self.PARTITION, item)
            return 201, {"statusDescription": "Item Created"}
        except ValueError as e:
            return 409, {"errorDescription": str(e)}
        except Exception as e:
            return 500, {"errorDescription": "Internal Server Error"}
