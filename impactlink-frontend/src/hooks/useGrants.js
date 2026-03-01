import { useState, useEffect } from "react";

export default function useGrants() {
  const [grants,      setGrants]   = useState([]);
  const [proposal,    setProposal] = useState(null);
  const [scoring,     setScoring]  = useState(null);
  const [hasRealData, setHasReal]  = useState(false);
  const [loading,     setLoading]  = useState(true);

  useEffect(() => {
    const storedMatches  = sessionStorage.getItem("matches");
    const storedProposal = sessionStorage.getItem("proposal");
    const storedScoring  = sessionStorage.getItem("scoring");

    if (storedMatches) {
      setGrants(JSON.parse(storedMatches));
      setProposal(JSON.parse(storedProposal));
      setScoring(JSON.parse(storedScoring));
      setHasReal(true);
      setLoading(false);
    } else {
      import("../services/mockData").then(m => {
        setGrants(m.mockGrants);
        setProposal(m.mockProfile);
        setHasReal(false);
        setLoading(false);
      });
    }
  }, []);

  return { grants, proposal, scoring, hasRealData, loading };
}