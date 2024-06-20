import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
interface StudentState {
  loading: boolean;
  success: boolean;
  error: string;
  data: {
    students: Array<{ full_name: string; password: string; username: string }>;
  };
  file_url: string;
  message: string;
}
interface CreateStudentDataArgs {
  students: string[];
  class_code: string;
}
interface ErrorResponse {
  response: {
    data: {
      message: string;
    };
  };
}
export const createStudentData = createAsyncThunk(
  "createStudent/createStudentData",
  async (
    { students, class_code }: CreateStudentDataArgs,
    { rejectWithValue }
  ) => {
    try {
      const token = localStorage.getItem("user-auth");
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_CREATE_STUDENTS_URL}`,
        {
          class_code: class_code,
          students,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const { data, file_url, class_name } = response.data;
      const { students: studentsData } = data;
      const newObject = {
        studentsCount: studentsData.length,
        file_url,
        students: studentsData,
        classTitle: class_name,
      };
      localStorage.setItem(
        "studentCreationResponse",
        JSON.stringify(newObject)
      );
      return response.data;
    } catch (err) {
      return rejectWithValue(err);
    }
  }
);
const initialState: StudentState = {
  loading: false,
  success: false,
  error: '',
  data: { students: [] },
  file_url: "",
  message: "",
};

const createStudent = createSlice({
  name: "createStudent",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(createStudentData.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(createStudentData.fulfilled, (state, action) => {
      state.loading = false;
      state.error = '';
      state.success = action.payload.success;
      state.message = action.payload.message;
      state.data = action.payload.data;
      state.file_url = action.payload.file_url;
    });
    builder.addCase(createStudentData.rejected, (state, action) => {
      state.loading = false;
      state.success = false;
      state.message = '';
      state.error = (action.payload as ErrorResponse)?.response?.data
        .message as string;
    });
  },
});

export default createStudent.reducer;
