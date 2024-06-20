import { configureStore } from '@reduxjs/toolkit'
import createClassReducer from './features/classroom/createClassSlice'
import classDetailsReducer from './features/classroom/classDetailSlice'
import createStudentReducer from './features/classroom/createStudentSlice'
import listStudentsReducer from './features/classroom/listStudentsSlice'
import removeStudentReducer from './features/classroom/removeStudentSlice'
import addStudentToClassReducer from './features/classroom/addStudentToClassSlice'
import listClassesReducer from './features/classroom/listClassesSlice'

export const store = configureStore({
    reducer: {
        createClass: createClassReducer,
        classDetails: classDetailsReducer,
        createStudent: createStudentReducer,
        listStudents: listStudentsReducer,
        removeStudents: removeStudentReducer,
        addStudentsToAnotherClass: addStudentToClassReducer,
        listClasses: listClassesReducer
    }
})

// Infer the type of makeStore
// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store['getState']>
export type AppDispatch = typeof store['dispatch']