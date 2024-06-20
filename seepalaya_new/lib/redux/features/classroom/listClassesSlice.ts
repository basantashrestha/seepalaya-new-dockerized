
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";

interface studentDetailsState {
  data: Array<{ classroom_code: string; classroom_title: string,student_count:number }>;
  loading: boolean;
  error: string | null;
  status: number;
}

interface ErrorResponse {
  data: {
    message: string;
  };
  status: number;
}
const initialState: studentDetailsState = {
  data: [],
  loading: false,
  error: null,
  status: 0,
};

export const fetchClasses = createAsyncThunk(
  "listClasses/fetchClasses",
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem("user-auth");
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_LIST_CLASSES_URL}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data.data;
    } catch (error: any) {
      const responseError: ErrorResponse = {
        data: {
          message: error.response.data.message,
        },
        status: error.response.status,
      };
      if (error.response.status === 401) {
        localStorage.removeItem("user-auth");
        localStorage.removeItem("studentCreationResponse");
        localStorage.removeItem("isTeacher");
        localStorage.removeItem("user");
      }

      return rejectWithValue(responseError);
    }
  }
);

const listClassesSlice = createSlice({
  name: "listClasses",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchClasses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchClasses.fulfilled, (state, action: PayloadAction<[]>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchClasses.rejected, (state, action) => {
        console.log(action.payload);
        const errorResponse = action.payload as ErrorResponse | undefined;
        state.loading = false;
        state.error = errorResponse?.data?.message ?? "An error occured";
        state.status = errorResponse?.status ?? 500;
      });
  },
});

export default listClassesSlice.reducer;
