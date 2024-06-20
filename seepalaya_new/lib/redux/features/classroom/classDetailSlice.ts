// lib/redux/features/classroom/classDetailsSlice.ts
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

interface ClassDetailsState {
  data: { title: string; studentsCount: number };
  loading: boolean;
  error: string | null;
  status: number ;
}

const initialState: ClassDetailsState = {
  data: {
    studentsCount: 0,
    title: "",
  },
  loading: false,
  error: null,
  status: 0,
};

export const fetchClassDetails = createAsyncThunk(
  "classroom/fetchClassDetails",
  async (classcode: string, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem("user-auth");
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_CLASSROOM_DETAILS_URL}`,
        {
          class_code: classcode,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
        
      );
      return response.data.data;
    } catch (error: any) {
      if (error.response.status === 401) {
        localStorage.removeItem("user-auth");
        localStorage.removeItem("studentCreationResponse");
        localStorage.removeItem("isTeacher");
        localStorage.removeItem("user");
        return rejectWithValue(error.response.status);
      }
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch class details"
      );
    }
  }
);

const classDetailsSlice = createSlice({
  name: "classDetails",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchClassDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchClassDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.data.title = action.payload.title;
        state.data.studentsCount = action.payload.student_count;
      })
      .addCase(fetchClassDetails.rejected, (state, action) => {
        console.log(action);
        state.loading = false;
        state.error = action.payload as string;
        state.status = action.payload as number;
      });
  },
});

export default classDetailsSlice.reducer;
