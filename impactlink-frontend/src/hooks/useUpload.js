import { useState } from "react";
import { uploadProposal } from "../services/api";

/**
 * useUpload
 * Handles PDF upload → backend pipeline → stores result in state
 * 
 * Returns:
 *   upload(file)   — call with a File object from input/drop
 *   proposal       — parsed proposal fields
 *   scoring        — scores + strengths/weaknesses
 *   matches        — RAG-matched grants array
 *   loading        — true while backend is processing
 *   error          — error message string or null
 *   reset()        — clear all state
 */
export default function useUpload() {
  const [proposal, setProposal] = useState(null);
  const [scoring,  setScoring]  = useState(null);
  const [matches,  setMatches]  = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  const upload = async (file) => {
    setLoading(true);
    setError(null);
    setProposal(null);
    setScoring(null);
    setMatches([]);

    try {
      const data = await uploadProposal(file);
      // Backend returns { proposal, scoring, matches }
      setProposal(data.proposal);
      setScoring(data.scoring);
      setMatches(data.matches || []);

      // Persist to sessionStorage so dashboard/grants pages can read it
      sessionStorage.setItem("proposal", JSON.stringify(data.proposal));
      sessionStorage.setItem("scoring",  JSON.stringify(data.scoring));
      sessionStorage.setItem("matches",  JSON.stringify(data.matches || []));
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setProposal(null);
    setScoring(null);
    setMatches([]);
    setError(null);
    sessionStorage.clear();
  };

  return { upload, proposal, scoring, matches, loading, error, reset };
}