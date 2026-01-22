from fastapi import APIRouter
from course.views.curd.create_course import create_course
from course.views.curd.add_video_course import add_video_to_course, get_course_videos
from course.views.curd.get_courses import get_courses, get_teacher_courses, search_courses
from course.views.curd.delete_course import delete_course
from course.views.curd.update_course import update_course
from course.views.enrollment import enroll_course, get_student_courses

router = APIRouter(prefix="/courses", tags=["Courses"])

# Course CRUD Operations (Teacher/Admin)
router.add_api_route("/all", get_courses, methods=["GET"])  # For student dashboard
router.add_api_route("/create", create_course, methods=["POST"])
router.add_api_route("/update", update_course, methods=["PUT"])
router.add_api_route("/add-video", add_video_to_course, methods=["POST"])
router.add_api_route("/videos/{course_id}", get_course_videos, methods=["GET"])
router.add_api_route("/delete", delete_course, methods=["DELETE"])

# Teacher specific routes
router.add_api_route("/teacher/{teacher_id}", get_teacher_courses, methods=["GET"])

# Student routes
router.add_api_route("/enroll", enroll_course, methods=["POST"])
router.add_api_route("/student/{student_id}", get_student_courses, methods=["GET"])

# Search functionality
router.add_api_route("/search/{query}", search_courses, methods=["GET"])