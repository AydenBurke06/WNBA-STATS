import dvpData from "@/data/dvp.json";
import DvpTable from "./components/DvpTable";

export default function Home() {
  return (
    <main className="page">
      <h1 className="title">Defense vs Position</h1>
      <p className="subtitle">What every WNBA team allows, by position, this season.</p>
      <DvpTable data={dvpData} />
    </main>
  );
}
