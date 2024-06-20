import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";

interface ClassData {
  title: string;
  class_code: string;
  teacher: string;
}
interface classState {
  loading: boolean;
  success: boolean;
  message: string;
  data: ClassData;
}

export const fetchClassData = createAsyncThunk("createClass/fetchClassData", async (classroom:string, { rejectWithValue }) => {
  try {
    const token = localStorage.getItem("user-auth");
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_CLASSROOM_URL}`,
      { title: classroom },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (err: any) {
    let errorMessage = "Encountered an error! Please try again later.";
    if (axios.isAxiosError(err)) {
      if (err.response?.data?.detail) {
        errorMessage = err.response?.data?.detail;
      } else {
        errorMessage = err.response?.data?.message;
      }
    }
    return rejectWithValue(errorMessage);
  }
});
const initialState: classState = {
  loading: false,
  success: false,
  message: "",
  data: {
    title: "",
    class_code: "",
    teacher: "",
  },
};

export const createClassSlice = createSlice({
  name: "createClass",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchClassData.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchClassData.fulfilled, (state, action) => {
      state.loading = false;
      state.success = true;
      (state.message = action.payload.message),
        (state.data = action.payload.data);
    });
    builder.addCase(fetchClassData.rejected, (state, action) => {
      state.loading = false;
      state.success = false;
      state.message = action.payload as string;
    });
  },
});

export default createClassSlice.reducer;
