export default function ProblemIntro() {
  return (
    <section
      id="about"
      className="scroll-mt-24 bg-white py-24 dark:bg-slate-950"
    >
      <div className="mx-auto grid max-w-7xl gap-12 px-5 lg:grid-cols-2 lg:px-8">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-red-600 dark:text-red-400">
            The operational challenge
          </p>

          <h2 className="mt-4 text-4xl font-black tracking-tight text-slate-950 dark:text-white">
            Separate alarms can share one underlying cause.
          </h2>
        </div>

        <div className="space-y-5 text-lg leading-8 text-slate-600 dark:text-slate-300">
          <p>
            Distributed network infrastructure can make it difficult to
            determine whether separate alarms come from individual towers or
            one shared network dependency.
          </p>

          <p>
            Without a connected view, operations teams spend valuable time
            piecing together signals while affected communities wait for clear
            information.
          </p>
        </div>
      </div>
    </section>
  )
}