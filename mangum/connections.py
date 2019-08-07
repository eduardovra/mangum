import typing
import os
from dataclasses import dataclass

import boto3
import botocore
from boto3.dynamodb.conditions import Attr

from mangum.exceptions import ConnectionTableException


@dataclass
class ConnectionTable:

    dynamodb = boto3.resource("dynamodb")

    def __post_init__(self) -> None:
        self.table = self.dynamodb.Table(os.environ["TABLE_NAME"])

    def get_item(self, connection_id: str) -> typing.Union[typing.Dict, None]:
        item = self.table.get_item(Key={"connectionId": connection_id}).get(
            "Item", None
        )
        return item

    def update_item(self, connection_id: str, **kwargs) -> int:
        result = self.table.put_item(Item={**{"connectionId": connection_id}, **kwargs})
        return result.get("ResponseMetadata", {}).get("HTTPStatusCode")

    def delete_item(self, connection_id: str) -> int:
        result = self.table.delete_item(Key={"connectionId": connection_id})
        return result.get("ResponseMetadata", {}).get("HTTPStatusCode")

    def get_group(self, group: str) -> typing.Union[typing.List[typing.Dict], None]:
        items = self.table.scan(
            ProjectionExpression="connectionId",
            FilterExpression=Attr("groups").contains(group),
        ).get("Items", None)
        return items

    def send(self, items: typing.List[typing.Dict], data: str) -> None:
        apigw_management = boto3.client(
            "apigatewaymanagementapi", endpoint_url=self.endpoint_url
        )
        for item in items:
            try:
                apigw_management.post_to_connection(
                    ConnectionId=item["connectionId"], Data=data
                )
            except botocore.exceptions.ClientError as exc:
                status_code = exc.response.get("ResponseMetadata", {}).get(
                    "HTTPStatusCode"
                )
                if status_code == 410:
                    # Delete stale connection
                    self.connection_table.delete_item(
                        Key={"connectionId": item["connectionId"]}
                    )
                else:
                    raise ConnectionTableException("Connection does not exist")
