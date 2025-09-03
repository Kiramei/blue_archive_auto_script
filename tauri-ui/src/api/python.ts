export interface PythonService {
  greet(name: string): Promise<string>;
}
