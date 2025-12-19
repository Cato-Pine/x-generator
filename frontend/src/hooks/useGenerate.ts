import { useMutation, useQueryClient } from '@tanstack/react-query';
import { generateApi } from '../api/client';
import type { GenerateRequest } from '../api/client';

export function useGenerate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GenerateRequest) =>
      generateApi.generate(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
}
