from rest_framework import serializers

class StudentOutputSerializer(serializers.Serializer):
        username = serializers.CharField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        password = serializers.CharField(read_only=True)

class TeacherStudentCreationOutputNestedSerializer(serializers.Serializer):
    students = StudentOutputSerializer(many=True)
    count = serializers.IntegerField()


class StudentInputSerializer(serializers.Serializer):
    full_name = serializers.CharField()


class TeacherStudentCreationInputNestedSerializer(serializers.Serializer):
    class_code = serializers.CharField()
    students = serializers.ListField(
        child=StudentInputSerializer()
    )

    def validate_students(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Cannot add more than 100 students at a time.")
        return value
