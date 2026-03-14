export interface User {
  user_id: string;
  name: string;
  status: string;
}

export interface CreateUserDto {
  user_id: string;
  name: string;
  status?: string;
}

export interface UpdateUserDto {
  name?: string;
  status?: string;
}