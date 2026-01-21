from fastapi import APIRouter
from course.views.create_course import create_course
from course.views.add_video_course import add_video_to_course
from course.views.get_courses import get_courses
from course.views.delete_course import delete_course
from course.views.update_course import update_course

router = APIRouter(prefix="/courses", tags=["Courses"])

router.add_api_route("/list", get_courses, methods=["GET"])
router.add_api_route("/create", create_course, methods=["POST"])
router.add_api_route("/update", update_course, methods=["PUT"])
router.add_api_route("/add-video", add_video_to_course, methods=["POST"])
router.add_api_route("/delete", delete_course, methods=["DELETE"])

