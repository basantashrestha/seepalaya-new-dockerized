import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
interface StudentState {
  loading: boolean;
  success: boolean;
  error: string;
  message: string;
}
interface CreateStudentDataArgs {
  title: string;
  class_code: string;
}
interface ErrorResponse {
  response: {
    data: {
      message: string;
    };
  };
}
export const updateClassInfoData = createAsyncThunk(
  "updateClassInfo/updateClassInfoData",
  async (
    { title, class_code }: CreateStudentDataArgs,
    { rejectWithValue }
  ) => {
    try {
      const token = localStorage.getItem("user-auth");
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_UPDATE_CLASS_INFO_URL}`,
        {
          class_code: class_code,
          title,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log('response from update class info ',response);
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

const updateClassInfoSlice = createSlice({
  name: "updateClassInfo",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(updateClassInfoData.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(updateClassInfoData.fulfilled, (state, action) => {
      state.loading = false;
      state.error = '';
      state.success = action.payload.success;
      state.message = action.payload.message;
    });
    builder.addCase(updateClassInfoData.rejected, (state, action) => {
      state.loading = false;
      state.success = false;
      state.message = '';
      state.error = (action.payload as ErrorResponse)?.response?.data
        .message as string;
    });
  },
});

export default updateClassInfoSlice.reducer;
