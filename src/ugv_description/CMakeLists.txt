cmake_minimum_required(VERSION 3.8)
project(ugv_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    urdf
    launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    ugv_description/rover_controller.py
    ugv_description/keyboard_teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
