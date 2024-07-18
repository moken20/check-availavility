import os
from typing import Any, Dict, List

from chalice import BadRequestError, Chalice, Rate, Response
from chalice.app import ConvertToMiddleware
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from chalicelib.ougatou_hotel import ScrapeOugatou
from chalicelib.util.dict_util import compare_lists_in_dict, to_message
from chalicelib.util.ssm_util import (get_parameter_store,
                                      update_parameter_store)
from aws_lambda_powertools import Logger 

app = Chalice(app_name="CheckAvailability")

logger = Logger()
app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context(log_event=True)))

handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))
linebot = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))


@app.schedule(Rate(10, unit=Rate.MINUTES))
def detect_availability_update(event) -> None:
    # get availability info
    outagou_hotel = ScrapeOugatou(start_date=None, end_date=None)
    new_availability = outagou_hotel.get_availability(filtering=True)
    old_availability = get_parameter_store(name="outagou_hotel")
    diff = compare_lists_in_dict(new=new_availability, old=old_availability)

    # send updated room
    if any(diff):
        logger.info(f'Updated room availability: {diff}')
        update_parameter_store(name="outagou_hotel", value=new_availability)
        send_line_message(hotel_name='王ヶ頭ホテル', availrooms=diff)


# Webhook
@app.route("/getavail", methods=["POST"])
def controller():
    logger.info("CALLED: controller()")

    # get X-Line-signature header value
    request = app.current_request
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.raw_body.decode("utf8")
    logger.info(f"REQUEST_BODY: {body}")

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        raise BadRequestError("InvalidSignatureError")

    return Response(body="Executed", status_code=200)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event) -> None:
    logger.info("CALLED: handle_message()")

    # get message.text
    received_text = event.message.text
    logger.info(f"RECEIVED_TEXT: {received_text}")

    outagou_hotel = ScrapeOugatou(start_date=None, end_date=None)
    new_availability = outagou_hotel.get_availability(filtering=True)

    # Reply message
    message = to_message(hotel_name='王ヶ頭ホテル', availrooms=new_availability)

    linebot.reply_message(
        reply_token=event.reply_token,
        messages=TextSendMessage(text=message),
    )


def send_line_message(hotel_name: str, availrooms: Dict[Any, List[Any]]) -> None:
    try:
        message = to_message(hotel_name=hotel_name, availrooms=availrooms)
        # Send message
        linebot.push_message(
            os.environ.get("LINE_USER_ID"), TextSendMessage(text=message)
        )
    except Exception as err:
        logger.exception(err)
        raise BadRequestError("Invalid Request.")
