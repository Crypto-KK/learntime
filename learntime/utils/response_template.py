from django.http import JsonResponse

success_response = JsonResponse({"status": "ok"})
fail_response = JsonResponse({"status": "fail"})
