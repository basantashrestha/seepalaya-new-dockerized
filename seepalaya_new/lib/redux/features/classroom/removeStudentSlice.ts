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
export const removeStudentData = createAsyncThunk(
  "removeStudent/removeStudentData",
  async (
    { students, class_code }: CreateStudentDataArgs,
    { rejectWithValue }
  ) => {
    try {
      const token = localStorage.getItem("user-auth");
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_REMOVE_STUDENTS_URL}`,
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
      console.log('response from removing students ',response);
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

const removeStudent = createSlice({
  name: "removeStudent",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(removeStudentData.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(removeStudentData.fulfilled, (state, action) => {
      state.loading = false;
      state.error = '';
      state.success = action.payload.success;
      state.message = action.payload.message;
    });
    builder.addCase(removeStudentData.rejected, (state, action) => {
      state.loading = false;
      state.success = false;
      state.message = '';
      state.error = (action.payload as ErrorResponse)?.response?.data
        .message as string;
    });
  },
});

export default removeStudent.reducer;
