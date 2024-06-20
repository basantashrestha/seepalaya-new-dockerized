from rest_framework import serializers

class StudentOutputSerializer(serializers.Serializer):
        user_type = serializers.CharField(read_only=True)
        username = serializers.CharField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        guardian_email = serializers.EmailField(read_only=True)
        user_email = serializers.EmailField(read_only=True)
        is_verified = serializers.CharField(read_only=True)

class TeacherStudentCreationOutputNestedSerializer(serializers.Serializer):
    students = StudentOutputSerializer(many=True)

class StudentInputSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()

class TeacherStudentCreationInputNestedSerializer(serializers.Serializer):
    students = serializers.ListField(
        child=StudentInputSerializer()
    )
