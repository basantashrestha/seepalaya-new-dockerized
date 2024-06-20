import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
interface StudentState {
  loading: boolean;
  success: boolean;
  error: string;
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
export const addStudent = createAsyncThunk(
  "addStudentToClass/addStudent",
  async (
    { students, class_code }: CreateStudentDataArgs,
    { rejectWithValue }
  ) => {
    try {
      const token = localStorage.getItem("user-auth");
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_ADD_STUDENTS_ANOTHER_CLASS_URL}`,
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
      console.log('response from adding students to class ',response);
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
  message: "",
};

const addStudentToClass = createSlice({
  name: "addStudentToClass",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(addStudent.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(addStudent.fulfilled, (state, action) => {
      state.loading = false;
      state.error = '';
      state.success = action.payload.success;
      state.message = action.payload.message;
    });
    builder.addCase(addStudent.rejected, (state, action) => {
      state.loading = false;
      state.success = false;
      state.message = '';
      state.error = (action.payload as ErrorResponse)?.response?.data
        .message as string;
    });
  },
});

export default addStudentToClass.reducer;
