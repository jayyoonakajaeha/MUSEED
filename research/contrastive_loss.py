import torch
import torch.nn as nn
import torch.nn.functional as F

class NTXentLoss(nn.Module):
    """
    Normalized Temperature-scaled Cross Entropy Loss (NT-Xent).
    Used in SimCLR and other contrastive learning frameworks.
    """
    def __init__(self, temperature=0.1):
        super(NTXentLoss, self).__init__()
        self.temperature = temperature

    def forward(self, z_i, z_j):
        """
        Args:
            z_i: Embeddings of the first view (batch_size, dim)
            z_j: Embeddings of the second view (batch_size, dim)
        """
        batch_size = z_i.shape[0]
        
        # Concatenate the representations: [z_i; z_j]
        # Shape: (2 * batch_size, dim)
        z = torch.cat([z_i, z_j], dim=0)
        
        # Normalize embeddings for cosine similarity
        z = F.normalize(z, dim=1, eps=1e-6)
        
        # Compute similarity matrix
        # Shape: (2*N, 2*N)
        sim_matrix = torch.matmul(z, z.T) / self.temperature
        
        # Mask-out self-contrast cases (diagonal)
        mask = torch.eye(2 * batch_size, dtype=torch.bool).to(z.device)
        
        # For each sample k, the positive is the corresponding augmented view.
        # If k < N, positive is k + N
        # If k >= N, positive is k - N
        # We can create a label tensor
        labels = torch.cat([torch.arange(batch_size) + batch_size, torch.arange(batch_size)], dim=0).to(z.device)
        
        # Remove self-similarity from the denominator calculation by setting diagonal to very small value
        # But CrossEntropyLoss expects logits.
        # The standard trick is to use the similarity matrix as logits, 
        # but ensure the diagonal (self) is not selected.
        # However, standard PyTorch CrossEntropy expects class indices.
        
        # Let's filter the similarity matrix to remove self-comparisons for the loss calculation logic
        # But using the mask approach with CrossEntropy is easier if we just mask the diagonal logits to -inf
        # Using -1e4 which is safe for float16 range (-6.5e4)
        sim_matrix.masked_fill_(mask, -1e4)
        
        loss = F.cross_entropy(sim_matrix, labels)
        return loss
