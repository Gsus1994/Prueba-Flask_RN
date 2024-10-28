// Frontend/App/Types/formTypes.tsx

export interface LoginResponse {
    access_token: string;
}

export interface LoginData {
    username: string;
    password: string;
}

export interface SignupResponse {
    msg: string;
}

export interface SignupData {
    confirmPassword: string;
    nombre: string;
    apellidos: string;
    dni: string;
    fecha_nacimiento: string;
    email: string;
    password: string;
    profile_image: {
        uri: string;
        name: string;
        type: string;
    };
}

export interface SignupFormInputs {
    dni: string;
    nombre: string;
    apellidos: string;
    email: string;
    password: string;
    confirmPassword: string;
    date?: Date;
    profileImage?: string;
}

export interface RecoveryFormData {
    email: string;
    code?: string;
    new_password?: string;
    confirm_password?: string;
}